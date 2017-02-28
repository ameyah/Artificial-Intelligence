import random

__author__ = 'ameya'


class Resolution:
    def __init__(self, people, tables):
        self.people = int(people)
        self.tables = int(tables)
        self.friends = []
        self.enemies = []
        self.clauses = set()

    def get_friends_enemies(self, input_data):
        for data in input_data:
            formatted_data = data.split(" ")
            d1 = formatted_data[0]
            d2 = formatted_data[1]
            if formatted_data[2] == "F":
                self.friends.append([d1, d2])
            elif formatted_data[2] == "E":
                self.enemies.append([d1, d2])

    def generate_cnf(self):
        # (Rule 1) CNF for all people
        for person in xrange(1, self.people + 1):
            clauses_a = []
            unique_clauses_b = []
            for table in xrange(1, self.tables + 1):
                clauses_a.append(int(str(person) + str(table)))  # appending tuples because we need to add it to set
                for tablej in range(table + 1, self.tables + 1):
                    unique_clauses_b.append((~int(str(person) + str(table)), ~int(str(person) + str(tablej)),))
            clauses_a = tuple(sorted(clauses_a))
            self.clauses.add(clauses_a)
            clauses_b = tuple(unique_clauses_b)
            if len(clauses_b) > 0:
                for clause in clauses_b:
                    self.clauses.add(tuple(sorted(clause)))

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
                self.clauses.add(tuple(sorted((~int(str(friend[0]) + str(table)), int(str(friend[1]) + str(table))))))
                self.clauses.add(tuple(sorted((int(str(friend[0]) + str(table)), ~int(str(friend[1]) + str(table))))))

        # (Rule 3) CNF for enemies
        for enemy in self.enemies:
            for table in xrange(1, self.tables + 1):
                self.clauses.add(tuple(sorted((~int(str(enemy[0]) + str(table)), ~int(str(enemy[1]) + str(table))))))

        print self.clauses

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

        """
        clauses = set()
        for i in xrange(len(ci)):
            for j in xrange(len(cj)):
                if ci[i] == ~cj[j]:
                    # TODO: Need to add try except?
                    ci_value = list(ci[0: i] + ci[i + 1: len(ci)])
                    cj_value = list(cj[0: j] + cj[j + 1: len(cj)])
                    combined_ci_cj = ci_value + cj_value
                    if len(combined_ci_cj) == 0:
                        return False
                    unique = []
                    [unique.append(item) for item in combined_ci_cj if item not in unique]
                    clauses.add(tuple(sorted(unique)))
                    # TODO: check the below condition
                    # elif ci_value != ~cj_value:
                    #     clauses.add((ci_value, cj_value))
        return clauses
        """

    @staticmethod
    def get_symbols(clauses):
        symbols = {}
        for clause in clauses:
            for symbol in clause:
                symbols[symbol] = random.choice([True, False])
                symbols[~symbol] = not symbols[symbol]
        return symbols

    def walksat(self, p=0.5, max_flips=10000):
        # extract symbols
        model = self.get_symbols(self.clauses)
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
    seating = r.walksat()
    keys = seating.keys()
    for key in keys:
        if key < 0:
            del seating[key]
    keys = sorted(seating.keys())
    for key in keys:
        if seating[key]:
            print str(key) + " : " + str(seating[key])