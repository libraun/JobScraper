# @ Author "Jet Braun"
#
# @ Institution "University of Minnesota-Duluth"
# @ File "include.py"
import csv

if __name__ == "__main__":

    with open("data.csv", 'r') as infile:
        reader = csv.reader(infile)
        cities = [row[7] for row in reader]
        with open("input.txt", 'w') as outfile:
            for loc in cities:
                outfile.write('{}\n'.format(loc.lower()))
            outfile.close()
        infile.close()
    