from decimal import Decimal
from time import time
from copy import deepcopy

__author__ = 'ameya'

TYPE_SEPARATOR = "******"
TABLE_SEPARATOR = "***"
DECISION_IDENTIFIER = "decision"


class Decision:
    def __init__(self):
        self.queries_p = []
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

    def add_queries(self, query_type, value):
        if query_type == "p":
            self.queries_p.append(value)
        elif query_type == "eu":
            self.queries_eu.append(value)
        elif query_type == "meu":
            self.queries_meu.append(value)

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

    def compute_p(self):
        for p in self.queries_p:

            if 'evidence' not in p:
                X = p['find'][0][0]
                XType = p['find'][0][1]
                e = {}
                for i in xrange(1, len(p['find'])):
                    e[p['find'][i][0]] = p['find'][i][1]
                print Decimal(self.enumeration_ask(X, XType, e)).quantize(Decimal("0.01"))
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
                print Decimal(result_numerator / result_denominator).quantize(Decimal("0.01"))


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
                if i in compare:
                    continue
                next_parents.extend(self.parents[i])
                variables.append(i)
            if not next_parents:
                break
            current_parents = deepcopy(next_parents)
        return variables[::-1]

    def enumeration_ask(self, X, XType, e):
        print (X, XType, e)
        variables = self.get_variables(X)
        for variable in e:
            variables.extend(self.get_variables(variable, variables))
        print variables
        return self.enumerate_all(variables, extend_dict(e, X, XType))

    def enumerate_all(self, variables, e):
        if not variables:
            return 1.0
        first = variables[0]
        rest = variables[1:]
        if first in e:
            prob = self.calc_prob(first, e[first], e)
            if prob == 0.0:
                # self.cache[str(variables) + str(e)] = 0.0
                return 0.0
            result = prob * self.enumerate_all(rest, e)
            # print first + str(e[first]) + str(e) + " " + str(result)
            # self.cache[str(variables) + str(e)] = result
            return result
        else:
            a = 0
            for possibility in self.possible_values:
                prob = self.calc_prob(first, possibility, e)
                if prob == 0.0:
                    # self.cache[str(variables) + str(e)] = 0.0
                    continue
                else:
                    a += prob * self.enumerate_all(rest, extend_dict(e, first, possibility))
                # print first + str(possibility) + str(e) + " " + str(a)

            result = a
            return result

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


def get_query_p_eu(line_formatted):
    split_evidence = line_formatted.split("|")
    queries = split_evidence[0].split(",")
    result_query = {'find': []}
    for query in queries:
        query_variable_value = query.split("=")
        if query_variable_value[1] == "+":
            query_variable_value[1] = True
        else:
            query_variable_value[1] = False
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


def get_query_meu(line_formatted):
    split_evidence = line_formatted.split("|")
    queries = split_evidence[0].split(",")
    result_query = {'find': queries}
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
                probability = get_query_p_eu(line_formatted[2:-1])
                decision.add_queries("p", probability)
            elif line_formatted[:3] == "EU(":
                expected_utility = get_query_p_eu(line_formatted[3:-1])
                decision.add_queries("eu", expected_utility)
            elif line_formatted[:4] == "MEU(":
                max_expected_utility = get_query_meu(line_formatted[4:-1])
                decision.add_queries("meu", max_expected_utility)
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
    start = time()
    lines = []
    decision = Decision()
    with open("input.txt", "r") as file_handler:
        lines = file_handler.readlines()
    lines = [i.strip() for i in lines]
    process_input(lines)
    print decision.variables
    print decision.parents
    decision.compute_p()
    print time() - start