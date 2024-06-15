# contains helper code available in evaluator
import io
import math

class DistanceMatrix:
    def __init__(self, loads, depot):
        self.distance_matrix = self.create_distance_matrix(loads, depot)

    def check_key(self, i, j):
        x, y = (i.x, i.y), (j.x, j.y)
        return (x, y) in self.distance_matrix or (y, x) in self.distance_matrix


    def get(self, i, j):
        x, y = (i.x, i.y), (j.x, j.y)
        if (x, y) in self.distance_matrix:
            return self.distance_matrix[(x, y)]
        return self.distance_matrix[(y, x)]

    def create_distance_matrix(self, loads, depot):
        distance_matrix = {}
        # calculate distances between each load's pickup and dropoff
        for load in loads:
            x, y = (load.pickup.x, load.pickup.y), (load.dropoff.x, load.dropoff.y)
            key = (x, y)
            distance_matrix[key] = distance(load.pickup, load.dropoff)
        # calculate distances between pickups and dropoffs from different loads
        # including depots
        pickups = [depot] + [load.pickup for load in loads]
        dropoffs = [depot] + [load.dropoff for load in loads]
        for pickup in pickups:
            for dropoff in dropoffs:
                x, y = (pickup.x, pickup.y), (dropoff.x, dropoff.y)
                key = (x, y)
                distance_matrix[key] = distance(pickup, dropoff)
        return distance_matrix

def distance(p1, p2):
    xDiff = p1.x - p2.x
    yDiff = p1.y - p2.y
    return math.sqrt(xDiff * xDiff + yDiff * yDiff)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point: ({self.x}, {self.y})'

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y

    def l(self):
        return (self.x, self.y)

    def toString(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

class Load:
    def __init__(self, id, pickup, dropoff):
        self.id = int(id)
        self.pickup = pickup
        self.dropoff = dropoff

    def __repr__(self):
        return f'Load: {self.id}, {self.pickup}, {self.dropoff}'

    def __str__(self):
        return f'{self.id=}, ({self.pickup}, {self.dropoff})'

class VRP:
    def __init__(self, loads):
        self.loads = loads
        self.h = {}
        self.h2 = {}

        for load in loads:
            self.h[load.id] = (load.pickup, load.dropoff)
            self.h2[(load.pickup, load.dropoff)] = load.id

    def pickup(self, id):
        return self.h[id]

    def __repr__(self):
        return 'VRP'

    def __str__(self):
        nl = '\n'
        return f'Loads: {[f'{s.__str__()}{nl}' for s in self.loads]}'

    def toProblemString(self):
        s = "loadNumber pickup dropoff\n"
        for idx, load in enumerate(self.loads):
            s += str(idx + 1) + " " + load.pickup.toString() + " " + load.dropoff.toString() + "\n"
        return s

class VRP2:
    def __init__(self, loads):
        self.h = {}
        self.h2 = {}
        self.loads = loads

        for load in loads:
            self.h[load.id] = load

    def pickup(self, id):
        return self.h[id]

    def idFromLoad(self, load):
        return self.h2[load]

    def __repr__(self):
        return 'VRP2'

    def __str__(self):
        nl = '\n'
        return f'Loads: {[f'{s.__str__()}{nl}' for s in self.loads]}'

    def toProblemString(self):
        s = "loadNumber pickup dropoff\n"
        for idx, load in enumerate(self.loads):
            s += str(idx + 1) + " " + load.pickup.toString() + " " + load.dropoff.toString() + "\n"
        return s

def loadProblemFromFile(filePath):
    f = open(filePath, "r")
    problemStr = f.read()
    f.close()
    return loadProblemFromProblemStr(problemStr)

def getPointFromPointStr(pointStr):
    pointStr = pointStr.replace("(", "").replace(")", "")
    splits = pointStr.split(",")
    return Point(float(splits[0]), float(splits[1]))

def loadProblemFromProblemStr(problemStr):
    loads = []
    buf = io.StringIO(problemStr)
    gotHeader = False
    while True:
        line = buf.readline()
        if not gotHeader:
            gotHeader = True
            continue
        if len(line) == 0:
            break
        line = line.replace("\n", "")
        splits = line.split()
        id = splits[0]
        pickup = getPointFromPointStr(splits[1])
        dropoff = getPointFromPointStr(splits[2])
        loads.append(Load(id, pickup, dropoff))
        # loads.append(Load(id, pickup, dropoff))
    return VRP2(loads)

def loadSolutionFromString(solutionStr):
    schedules = []
    buf = io.StringIO(solutionStr)
    while True:
        line = buf.readline()
        if len(line) == 0:
            break
        if ('[' not in line) or (']' not in line):
            return schedules, "Solution format incorrect. Expected all lines to be in format [{load_id}, {load_id}, ...], but got this: " + line
        line = line.replace('[', '')
        line = line.replace(']', '')
        line = line.replace('\n', '')
        line = line.replace(' ', '')
        splits = line.split(',')
        schedule = []
        for loadID in splits:
            schedule.append(loadID)
        schedules.append(schedule)
    return schedules, ""

def loadCountOrAssignmentError(problem, solutionSchedules):
    solutionLoadIDs = {}
    for schedule in solutionSchedules:
        for loadID in schedule:
            if loadID in solutionLoadIDs:
                return "load " + loadID + " was included in at least two driver schedules"
            solutionLoadIDs[loadID] = True

    if len(solutionLoadIDs) != len(problem.loads):
        return "the solution load count is not equal to the problem load count"

    for load in problem.loads:
        if load.id not in solutionLoadIDs:
            return "load " + load.id + " was not assigned to a driver"

    return ""
