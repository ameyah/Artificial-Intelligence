from decimal import Decimal
from time import time
from copy import deepcopy
import itertools

__author__ = 'ameya'

TYPE_SEPARATOR = "******"
TABLE_SEPARATOR = "***"
DECISION_IDENTIFIER = "decision"


class Decision:
    def __init__(self):
        self.queries = []
        self.queries_eu = []
        self.queries_meu = []
        self.cpts = {}
        self.parents = {}
        self.variables = []
        self.decision_nodes = []
        self.utility_parents = []
        self.utility_values = {}
        self.possible_values = [True, False]
        self.cache = {}
        self.result = []

    def add_queries(self, value):
        self.queries.append(value)

    def add_parents(self, node, parents):
        self.parents[node] = parents

    def add_cpt(self, node, node_cpt):
        self.cpts[node] = node_cpt

    def add_decision_node(self, node):
        self.decision_nodes.append(node)

    def add_utility_parents(self, parents):
        self.utility_parents = parents

    def set_utility_values(self, values):
        self.utility_values = values

    def add_variable(self, node):
        self.variables.append(node)

    def generate_cache_key(self, var, rest, e):
        parents_values = ()
        for parent in self.parents[var]:
            parents_values += ((parent, e[parent],),)
        var_index = self.variables.index(var)
        topological_order = ()
        for i in rest:
            for parent in self.parents[i]:
                if self.variables.index(parent) < var_index:
                    topological_order += ((parent, e[parent],),)
        """
        if var in e:
            cache_key = (var, e[var], parents_values,)
        else:
            cache_key = (var, None, parents_values,)
        """
        cache_key = (var, topological_order, parents_values,)
        return cache_key

    def process_queries(self):
        for q in self.queries:
            if q['type'] == "P":
                self.result.append(str(Decimal(str(self.compute_probability(q))).quantize(Decimal("0.01"))))
            elif q['type'] == "EU":
                self.result.append(str(int(round(self.calculate_eu(q)))))
            elif q['type'] == "MEU":
                result = self.compute_meu(q)
                print_result = ""
                for permutation in result[0]:
                    if permutation:
                        print_result += "+ "
                    else:
                        print_result += "- "
                print_result += str(int(round(result[1])))
                self.result.append(print_result)

    def print_result(self):
        with open("output.txt", "w") as file_handler:
            for i in xrange(len(self.result) - 1):
                file_handler.write(self.result[i] + "\n")
            file_handler.write(self.result[len(self.result) - 1])

    def calc_prob(self, node, val, e):
        if node in self.decision_nodes:
            return 1.0
        cpt_key = [e[i] for i in self.parents[node]]
        cpt_key = tuple(cpt_key)
        return self.cpts[node][cpt_key] if val else 1 - self.cpts[node][cpt_key]

    def get_variables(self, X, compare=list()):
        variables = []
        current_parents = [X]
        while True:
            next_parents = []
            for i in current_parents:
                if i in compare or i in variables:
                    continue
                next_parents.extend(self.parents[i])
                variables.append(i)
            if not next_parents:
                break
            current_parents = deepcopy(next_parents)
        return variables[::-1]

    def enumeration_ask(self, X, XType, e):

        self.cache = {}

        variables = self.get_variables(X)
        for variable in e:
            variables.extend(self.get_variables(variable, variables))
        # print "variables" + str(variables)
        op_variables = []
        for variable in self.variables:
            if variable in variables:
                op_variables.append(variable)
        return self.enumerate_all(op_variables, extend_dict(e, X, XType))

    def enumerate_all(self, variables, e):
        if not variables:
            return 1.0
        first = variables[0]
        rest = variables[1:]
        cache_key = self.generate_cache_key(first, rest, e)
        if cache_key in self.cache:
            # print cache_key
            return self.cache[cache_key]
        if first in e:
            prob = self.calc_prob(first, e[first], e)
            if prob == 0.0:
                return 0.0
            result = prob * self.enumerate_all(rest, e)
            return result
        else:
            a = 0
            for possibility in self.possible_values:
                prob = self.calc_prob(first, possibility, e)
                rest_result = self.enumerate_all(rest, extend_dict(e, first, possibility))
                a += prob * rest_result

            result = a
            x = self.generate_cache_key(first, rest, e)
            self.cache[x] = result
            # print self.cache
            return result

    def compute_probability(self, p):
        if 'evidence' not in p:
            X = p['find'][0][0]
            XType = p['find'][0][1]
            e = {}
            for i in xrange(1, len(p['find'])):
                e[p['find'][i][0]] = p['find'][i][1]
            return self.enumeration_ask(X, XType, e)
        else:

            X = p['find'][0][0]
            XType = p['find'][0][1]
            e = {}
            for i in xrange(1, len(p['find'])):
                e[p['find'][i][0]] = p['find'][i][1]
            for i in xrange(len(p['evidence'])):
                e[p['evidence'][i][0]] = p['evidence'][i][1]
            result_numerator = self.enumeration_ask(X, XType, e)

            X = p['evidence'][0][0]
            XType = p['evidence'][0][1]
            e = {}
            for i in xrange(1, len(p['evidence'])):
                e[p['evidence'][i][0]] = p['evidence'][i][1]
            result_denominator = self.enumeration_ask(X, XType, e)

            return result_numerator / result_denominator

    def calculate_eu(self, p):
        result_utility = 0.0
        utility_p = {'find': [], 'evidence': p['find']}  # Init with p['find']
        parent_truth_mapping = {}
        if 'evidence' in p:
            for evidence in p['evidence']:
                utility_p['evidence'].extend([evidence])

        for parent in self.utility_parents:
            if [parent, True] not in utility_p['evidence'] and [parent, False] not in utility_p['evidence']:
                utility_p['find'].append([parent, None])
            else:
                parent_truth_mapping[parent] = None

        # Fill in values in parent_truth_mapping
        for evidence in utility_p['evidence']:
            if evidence[0] in parent_truth_mapping:
                parent_truth_mapping[evidence[0]] = evidence[1]

        if len(utility_p['find']) > 0:
            for permutation in itertools.product(self.possible_values, repeat=len(utility_p['find'])):
                for i in xrange(len(utility_p['find'])):
                    utility_p['find'][i][1] = permutation[i]
                ordered_permutations = ()
                j = 0
                for i in self.utility_parents:
                    if i in parent_truth_mapping:
                        ordered_permutations += (parent_truth_mapping[i],)
                    else:
                        ordered_permutations += (permutation[j],)
                        j += 1
                result_utility += self.utility_values[ordered_permutations] * self.compute_probability(utility_p)
            return result_utility
        else:
            permutation = ()
            for parent in self.utility_parents:
                for var_arr in utility_p['evidence']:
                    if var_arr[0] == parent:
                        utility_p['find'].append([parent, var_arr[1]])
                        permutation += (var_arr[1],)
            result_utility = self.utility_values[permutation] * self.compute_probability(utility_p)
            return result_utility

    def compute_meu(self, p):
        permutation_count = 0
        input_find = deepcopy(p['find'])
        result_fixed_values = {}
        for i in xrange(len(p['find']) - 1, -1, -1):
            if p['find'][i][1] is None:
                permutation_count += 1
            else:
                if 'evidence' not in p:
                    p['evidence'] = []
                p['evidence'].append(p['find'][i])
                result_fixed_values[p['find'][i][0]] = i
                del p['find'][i]
        max_eu = 0
        max_key = ()
        for permutation in itertools.product(self.possible_values, repeat=permutation_count):
            for i in xrange(len(p['find'])):
                p['find'][i][1] = permutation[i]
            eu = self.calculate_eu(deepcopy(p))
            if eu > max_eu:
                max_eu = eu
                max_key = ()
                i = 0
                for input_var in input_find:
                    if input_var[1] is None:
                        max_key += (permutation[i],)
                        i += 1
                    else:
                        max_key += (input_var[1],)
        return [max_key, max_eu]

    """
    def elimination_ask(self, X, XType, e):
        factors = []
        for var in reversed(self.variables):
            factors.append(self.make_factor(var, e))
            if var != X and var not in e:
                factors = self.sum_out(var, factors)
        return pointwise_product(factors).normalize()

    def sum_out(self, var, factors):
        result, var_factors = [], []
        for f in factors:
            (var_factors if var in f.variables else result).append(f)
        result.append(pointwise_product(var_factors).sum_out(var, factors))
        return result

    def make_factor(self, var, e):
        variables = [X for X in [var] + self.parents[var] if X not in e]
        cpt = {self.event_values(e1, variables): self.calc_prob(var, e1[var], e1)
               for e1 in self.all_events(variables, e)}
        return Factor(variables, cpt)

    def all_events(self, variables, e):
        if not variables:
            yield e
        else:
            X, rest = variables[0], variables[1:]
            for e1 in self.all_events(rest, e):
                for x in self.possible_values:
                    yield extend_dict(e1, X, x)

    def event_values(self, event, variables):
        if isinstance(event, tuple) and len(event) == len(variables):
            return event
        else:
            return tuple([event[var] for var in variables])
    """


def pointwise_product(factors):
    return reduce(lambda f, g: f.pointwise_product(g), factors)


def extend_dict(old_dict, key, val):
    new_dict = old_dict.copy()
    new_dict[key] = val
    return new_dict


def get_query(line_formatted, query_type):
    split_evidence = line_formatted.split("|")
    queries = split_evidence[0].split(",")
    result_query = {'find': [], 'type': query_type}
    for query in queries:
        query_variable_value = query.split("=")
        if len(query_variable_value) > 1:
            if query_variable_value[1] == "+":
                query_variable_value[1] = True
            elif query_variable_value[1] == "-":
                query_variable_value[1] = False
        else:
            query_variable_value.append(None)
        result_query['find'].append(query_variable_value)
    if len(split_evidence) == 2:
        # to calculate conditional probability
        evidence = split_evidence[1].split(",")
        result_query['evidence'] = []
        for e in evidence:
            evidence_variable_value = e.split("=")
            if evidence_variable_value[1] == "+":
                evidence_variable_value[1] = True
            else:
                evidence_variable_value[1] = False
            result_query['evidence'].append(evidence_variable_value)
    return result_query


def process_input(lines):
    table_start_flag = False
    utility_start_flag = False
    i = 0
    while i < len(lines):
        if lines[i] == TYPE_SEPARATOR:
            if table_start_flag:
                table_start_flag = False
                utility_start_flag = True
            else:
                table_start_flag = True
            i += 1
            continue
        if not table_start_flag or not utility_start_flag:
            line_formatted = "".join(lines[i].split())
        if not table_start_flag and not utility_start_flag:
            if line_formatted[:2] == "P(":
                probability = get_query(line_formatted[2:-1], query_type="P")
                decision.add_queries(probability)
            elif line_formatted[:3] == "EU(":
                expected_utility = get_query(line_formatted[3:-1], query_type="EU")
                decision.add_queries(expected_utility)
            elif line_formatted[:4] == "MEU(":
                max_expected_utility = get_query(line_formatted[4:-1], query_type="MEU")
                decision.add_queries(max_expected_utility)
            i += 1
            continue
        elif table_start_flag:
            # store CPT's
            cpt_2d = lines[i].split("|")
            cpt_2d = [j.strip() for j in cpt_2d]
            decision.add_parents(cpt_2d[0], list())
            decision.add_variable(cpt_2d[0])
            if len(cpt_2d) == 2:
                cpt_dependencies = cpt_2d[1].split(" ")
                decision.add_parents(cpt_2d[0], cpt_dependencies)
            i += 1
            cpt = {}
            while i < len(lines):
                if lines[i] == TYPE_SEPARATOR or lines[i] == TABLE_SEPARATOR:
                    if lines[i] == TABLE_SEPARATOR:
                        i += 1
                    break
                elif lines[i] == DECISION_IDENTIFIER:
                    decision.add_decision_node(cpt_2d[0])
                    i += 1
                    if lines[i] == TABLE_SEPARATOR:
                        i += 1
                    break
                else:
                    cpt_row = lines[i].strip().split(" ")
                    cpt_row[1:] = [True if cpt_row[j] == "+" else False for j in xrange(1, len(cpt_row))]
                    cpt[tuple(cpt_row[1:])] = float(cpt_row[0])
                    i += 1
            decision.add_cpt(cpt_2d[0], cpt)
        elif utility_start_flag:
            utility_parents = lines[i].split("|")[1].strip()
            utility_parents = utility_parents.split(" ")
            decision.add_utility_parents(utility_parents)
            i += 1
            utility_values = {}
            while i < len(lines):
                utility_row = lines[i].strip().split(" ")
                utility_row[1:] = [True if utility_row[j] == "+" else False for j in xrange(1, len(utility_row))]
                utility_values[tuple(utility_row[1:])] = float(utility_row[0])
                i += 1
            decision.set_utility_values(utility_values)


if __name__ == '__main__':
    lines = []
    decision = Decision()
    with open("input.txt", "r") as file_handler:
        lines = file_handler.readlines()
    lines = [i.strip() for i in lines]
    process_input(lines)
    decision.process_queries()
    decision.print_result()