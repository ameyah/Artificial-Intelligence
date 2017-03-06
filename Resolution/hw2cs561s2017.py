import random
from copy import deepcopy

__author__ = 'ameya'


class Resolution:
    def __init__(self, people, tables):
        self.people = int(people)
        self.tables = int(tables)
        self.friends = []
        self.enemies = []
        self.clauses = []
        self.person_separator = 1000
        self.count = 0
        self.related_people = set()

    def get_related_people(self):
        return self.related_people

    def get_friends_enemies(self, input_data):
        for data in input_data:
            formatted_data = data.split(" ")
            d1 = int(formatted_data[0])
            d2 = int(formatted_data[1])
            if d1 > self.people or d2 > self.people:
                continue
            self.related_people.add(d1)
            self.related_people.add(d2)
            if formatted_data[2].lower() == "f":
                self.friends.append([d1, d2])
            elif formatted_data[2].lower() == "e":
                self.enemies.append([d1, d2])

    def generate_cnf(self):
        # (Rule 1) CNF for all people
        for person in self.related_people:
            clauses_a = []
            for table in xrange(1, self.tables + 1):
                clauses_a.append(
                    (person * self.person_separator) + table)  # appending tuples because we need to add it to set
            self.clauses.append(clauses_a)
        for person in self.related_people:
            for table in xrange(1, self.tables + 1):
                for tablej in range(table + 1, self.tables + 1):
                    self.clauses.append([~((person * self.person_separator) + table),
                                         ~((person * self.person_separator) + tablej)])

        # (Rule 2) CNF for friends
        """
        for friend in self.friends:
            for tablei in xrange(1, self.tables + 1):
                for tablej in xrange(1, self.tables + 1):
                    if tablei != tablej:
                        self.clauses.add((~int(str(friend[0]) + str(tablei)), ~int(str(friend[1]) + str(tablej))))
        """
        for friend in self.friends:
            for table in xrange(1, self.tables + 1):
                self.clauses.append([~((friend[0] * self.person_separator) + table),
                                     ((friend[1] * self.person_separator) + table)])
                self.clauses.append([((friend[0] * self.person_separator) + table),
                                     ~((friend[1] * self.person_separator) + table)])

        # (Rule 3) CNF for enemies
        for enemy in self.enemies:
            for table in xrange(1, self.tables + 1):
                self.clauses.append(
                    [~((enemy[0] * self.person_separator) + table), ~((enemy[1] * self.person_separator) + table)])

    def pl_resolution(self):
        while True:
            new = set()
            clauses = list(self.clauses)
            for i in xrange(len(clauses) - 1):
                for j in xrange(i + 1, len(clauses)):
                    resolvents = self.pl_resolve(clauses[i], clauses[j])
                    if resolvents == False:
                        return False
                    new = new.union(resolvents)
            if new.issubset(self.clauses):
                return True
            self.clauses = self.clauses.union(new)
            print len(self.clauses)

    @staticmethod
    def pl_resolve(ci, cj):
        clauses = set()
        for i in xrange(len(ci)):
            for j in xrange(len(cj)):
                if ci[i] == ~cj[j] or ~ci[i] == cj[j]:
                    # TODO: Need to add try except?
                    ci_value = list(ci[0: i] + ci[i + 1: len(ci)])
                    cj_value = list(cj[0: j] + cj[j + 1: len(cj)])
                    combined_ci_cj = ci_value + cj_value
                    if len(combined_ci_cj) == 0:
                        print ci
                        print cj
                        return False
                    unique = []
                    for item in combined_ci_cj:
                        if item not in unique:
                            if ~item in unique:
                                unique = []
                                break
                            else:
                                unique.append(item)
                    if len(unique) > 0:
                        clauses.add((tuple(sorted(unique))))
        return clauses

    @staticmethod
    def get_walksat_model(clauses):
        symbols = {}
        for clause in clauses:
            for symbol in clause:
                symbols[symbol] = random.choice([True, False])
                symbols[~symbol] = not symbols[symbol]
        return symbols

    @staticmethod
    def get_symbols(clauses):
        symbols = set()
        for clause in clauses:
            for symbol in clause:
                symbols.add(symbol)
        return symbols

    @staticmethod
    def check_satisfiability(clause, model, empty_symbol_check):
        for symbol in clause:
            if symbol in model:
                if model[symbol]:
                    return True
                else:
                    continue
            else:
                if empty_symbol_check:
                    return None
        return False

    @staticmethod
    def get_pure_symbol(clauses, model):
        # new_clauses = deepcopy(clauses)
        possible_pure_symbols = set()
        for clause in clauses:
            temp_pure_symbols = set()
            clause_true_flag = False
            for literal in clause:
                if literal in model:
                    if model[literal]:
                        # temp_pure_symbols = set()
                        clause_true_flag = True
                        break
                else:
                    temp_pure_symbols.add(literal)
            if not clause_true_flag:
                possible_pure_symbols = possible_pure_symbols.union(temp_pure_symbols)

        # send positive symbols first as per optimization given in AIMA Java code
        try:
            pure_symbols_positive = set()
            pure_symbols_negative = set()
            for literal in possible_pure_symbols:
                if ~literal not in possible_pure_symbols:
                    if literal > 0:
                        pure_symbols_positive.add(literal)
                    else:
                        pure_symbols_negative.add(literal)
            if len(pure_symbols_positive) > 0:
                return list(pure_symbols_positive)
            else:
                return list(pure_symbols_negative)
                # return list(possible_pure_symbols)
        except:
            return []

    @staticmethod
    def get_unit_clause(clauses, model):
        for clause in clauses:
            count_unknown = 0
            unit_clause = None
            true_flag = False
            for literal in clause:
                if literal in model:
                    if model[literal]:
                        true_flag = True
                        break
                else:
                    count_unknown += 1
                    unit_clause = literal
                    if count_unknown == 2:
                        break
            if count_unknown == 1:
                if not true_flag:
                    return unit_clause
        return False

    @staticmethod
    def unit_clause_rule_remove(clauses, p):
        clause_remove = []
        for i in xrange(len(clauses)):
            literal_remove = []
            for j in xrange(len(clauses[i])):
                if clauses[i][j] == ~p:
                    literal_remove.append(j)
                elif clauses[i][j] == p:
                    clause_remove.append(i)
                    literal_remove = []
                    break
            for j in sorted(literal_remove, reverse=True):
                del clauses[i][j]
        for i in sorted(clause_remove, reverse=True):
            del clauses[i]

    def run_dpll(self):
        return self.dpll(self.clauses, self.get_symbols(self.clauses), {})

    def dpll(self, clauses, symbols, model):
        # check if all clauses are true
        sat_flag = True
        for clause in clauses:
            if self.check_satisfiability(clause, model, False):
                continue
            else:
                sat_flag = False
                break
        if sat_flag:
            return True, model

        # check if a clause is false
        sat_flag = True
        for clause in clauses:
            sat_check = self.check_satisfiability(clause, model, True)
            if sat_check:
                continue
            elif sat_check is None:
                break
            else:
                sat_flag = False
                break
        if not sat_flag:
            return False, {}

        pure_symbols = self.get_pure_symbol(clauses, model)
        if len(pure_symbols) > 0:
            # print pure_symbols
            for p in pure_symbols:
                symbols.remove(p)
                symbols.discard(~p)
                model[p] = True
                model[~p] = False
            return self.dpll(clauses, symbols, model)

        p = self.get_unit_clause(clauses, model)
        if p:
            symbols.remove(p)
            symbols.discard(~p)
            model[p] = True
            model[~p] = False
            return self.dpll(clauses, symbols, model)

        new_symbols_true = deepcopy(symbols)
        p = new_symbols_true.pop()
        new_symbols_false = deepcopy(new_symbols_true)

        new_symbols_true.discard(~p)
        model_true = deepcopy(model)
        model_true[p] = True
        model_true[~p] = False
        res_true, model_true = self.dpll(clauses, new_symbols_true, model_true)
        if res_true:
            return True, model_true

        model_false = deepcopy(model)
        model_false[p] = False
        model_false[~p] = True
        new_symbols_false.discard(~p)
        res_false, model_false = self.dpll(clauses, new_symbols_false, model_false)
        if res_false:
            return True, model_false
        return False, {}

    def walksat(self, p=0.5, max_flips=10000):
        # extract symbols
        model = self.get_walksat_model(self.clauses)
        for i in xrange(max_flips):
            unsatisfied_clauses = []
            for clause in self.clauses:
                false_flag = True
                for item in clause:
                    if model[item]:
                        false_flag = False
                        break
                if false_flag:
                    unsatisfied_clauses.append(clause)

            if len(unsatisfied_clauses) == 0:
                print "iteration: " + str(i)
                return model
            random_clause = random.choice(unsatisfied_clauses)
            if p > random.uniform(0.0, 1.0):
                random_symbol = random.choice(random_clause)
                model[random_symbol] = not model[random_symbol]
                model[~random_symbol] = not model[~random_symbol]
            else:
                # Flip the symbol in clause that maximizes number of sat. clauses
                max_satisfied_clauses = -1
                satisfied_symbol = None
                for symbol in random_clause:
                    model[symbol] = not model[symbol]
                    model[~symbol] = not model[~symbol]
                    satisfied_clauses = 0
                    for clause in self.clauses:
                        for item in clause:
                            if model[item]:
                                satisfied_clauses += 1
                                break
                    if satisfied_clauses > max_satisfied_clauses:
                        max_satisfied_clauses = satisfied_clauses
                        satisfied_symbol = symbol
                    model[symbol] = not model[symbol]
                    model[~symbol] = not model[~symbol]

                model[satisfied_symbol] = not model[satisfied_symbol]
                model[~satisfied_symbol] = not model[~satisfied_symbol]

        return False


def write_output_file(answer, model, related_people):
    global people
    with open("output.txt", "w") as op_file_handler:
        if answer:
            op_file_handler.write("yes")
            people_tables = []
            for i in xrange(1, int(people) + 1):
                if i not in related_people:
                    people_tables.append((i * 1000) + 1)
            for p_t in model:
                if p_t > 0 and model[p_t]:  # should be positive and True
                    people_tables.append(p_t)
            people_tables = sorted(people_tables)
            for p_t in people_tables:
                person = p_t / 1000
                table = p_t % 1000
                op_file_handler.write("\n" + str(person) + " " + str(table))
        else:
            op_file_handler.write("no")


if __name__ == '__main__':
    lines = []
    with open("input.txt", "r") as file_handler:
        lines = file_handler.readlines()
    lines = [line.strip() for line in lines]
    people, tables = lines[0].split(" ")
    r = Resolution(people, tables)
    r.get_friends_enemies(lines[1:])
    r.generate_cnf()
    # result = r.pl_resolution()
    output, final_model = r.run_dpll()
    related_people = r.get_related_people()
    write_output_file(output, final_model, related_people)
    """
    seating = r.walksat()
    keys = seating.keys()
    for key in keys:
        if key < 0:
            del seating[key]
    keys = sorted(seating.keys())
    for key in keys:
        if seating[key]:
            print str(key) + " : " + str(seating[key])
    """