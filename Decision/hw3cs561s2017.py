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
        self.utility_parents = []
        self.utility_values = {}

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

    def add_utility_parents(self, parents):
        self.utility_parents = parents

    def set_utility_values(self, values):
        self.utility_values = values


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


if __name__ == '__main__':
    lines = []
    decision = Decision()
    with open("input.txt", "r") as file_handler:
        lines = file_handler.readlines()
    lines = [i.strip() for i in lines]
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
            if len(cpt_2d) == 2:
                cpt_dependencies = cpt_2d[1].split(" ")
                decision.add_parents(cpt_2d[0], cpt_dependencies)
            i += 1
            cpt = {}
            continue_flag = False
            while i < len(lines):
                if lines[i] == TYPE_SEPARATOR or lines[i] == TABLE_SEPARATOR:
                    if lines[i] == TABLE_SEPARATOR:
                        i += 1
                    continue_flag = True
                    break
                elif lines[i] == DECISION_IDENTIFIER:
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