# Program ParkingSystemITB
# Simulates ITB Jatinangor campus parking using a synthesized dataset.
# The user picks a DESTINATION BUILDING; the program outputs the nearest parking that still
# has a free public slot (Euclidean distance, step-by-step nearest neighbor search).
# Buildings and parking lots are separate datasets (parking is not tied to a building).
# Lecturer slots are reserved out of each lot's capacity first; free public slots are then
# generated randomly inside the remaining public capacity using randint.

from random import randint

# DECLARATIONS
# NB, NP, i : int                                   (number of buildings / parking lots / loop counter)
# buildings : array [0..NB-1] of string
# bld_x, bld_y : array [0..NB-1] of float
# lots, lot_type : array [0..NP-1] of string
# lot_x, lot_y : array [0..NP-1] of float
# capacity : array [0..NP-1] of int
# LECT_PCT : array [0..2] of int                    (% of a lot reserved per time block)
# lecturer_schedule : array [0..NP-1][0..2] of int
# public_cap, available, active_reserved : array [0..NP-1] of int
# current_hour, target_no, target_idx, nearest_idx : int
# dist : float
# running : bool
# choice : string


# Function Definition: CalculateDistance
def CalculateDistance(x1, y1, x2, y2):
    # returns the 2D Euclidean distance between (x1, y1) and (x2, y2)

    # LOCAL DECLARATIONS
    # dx, dy : float

    # ALGORITHM
    dx = x2 - x1
    dy = y2 - y1
    return ((dx * dx) + (dy * dy)) ** 0.5


# Function Definition: GetTimeSlot
def GetTimeSlot(current_hour):
    # returns the time block index (0-2) that current_hour (0-23) falls in

    # LOCAL DECLARATIONS

    # ALGORITHM
    if (current_hour >= 0 and current_hour < 8):
        return 0  # Before Lectures / Off-Peak (00:00 - 07:59)
    elif (current_hour >= 8 and current_hour < 13):
        return 1  # Lecture Hours (08:00 - 13:00)
    else:
        return 2  # After Lectures / Off-Peak (13:00 - 23:59)


# Function Definition: ReadWholeNumber
def ReadWholeNumber(prompt, low, high):
    # returns a whole number between low and high (inclusive); keeps asking until the input is valid

    # LOCAL DECLARATIONS
    # raw : string

    # ALGORITHM
    raw = input(prompt)
    # isdigit() is checked first so int(raw) is never called on text like "abc" or "-3"
    while (raw.isdigit() == False or int(raw) < low or int(raw) > high):
        raw = input("Invalid input. " + prompt)
    return int(raw)


# Procedure Definition: BuildLecturerSchedule
def BuildLecturerSchedule(lecturer_schedule, capacity, LECT_PCT, NP):
    # fills the 2D schedule: slots reserved for lecturers per lot per time block

    # LOCAL DECLARATIONS
    # i, s : int

    # ALGORITHM
    for i in range(NP):
        for s in range(3):
            lecturer_schedule[i][s] = (capacity[i] * LECT_PCT[s]) // 100
    return


# Procedure Definition: ApplyLecturerReservation
def ApplyLecturerReservation(capacity, lecturer_schedule, active_reserved, public_cap, current_hour, NP):
    # locks the lecturer slots of the active time block, then derives the PUBLIC capacity.
    # This runs BEFORE availability is randomized, so reservations never depend on random luck.

    # LOCAL DECLARATIONS
    # i, slot, lock : int

    # ALGORITHM
    slot = GetTimeSlot(current_hour)
    for i in range(NP):
        lock = lecturer_schedule[i][slot]
        if (lock > capacity[i]):
            lock = capacity[i]
        active_reserved[i] = lock
        public_cap[i] = capacity[i] - lock
    return


# Procedure Definition: InitAvailability
def InitAvailability(available, public_cap, NP):
    # randomly populates free PUBLIC slots; can never exceed what the public pool allows

    # LOCAL DECLARATIONS
    # i : int

    # ALGORITHM
    for i in range(NP):
        available[i] = randint(0, public_cap[i])
    return


# Procedure Definition: DisplayBuildings
def DisplayBuildings(buildings, NB):
    # lists every selectable destination building with its number

    # LOCAL DECLARATIONS
    # i : int

    # ALGORITHM
    print("\n------------------------------ DESTINATION BUILDINGS ------------------------------")
    for i in range(NB):
        print("[" + str(i + 1) + "] " + buildings[i])
    print("-----------------------------------------------------------------------------------\n")
    return


# Procedure Definition: DisplayParkingStatus
def DisplayParkingStatus(lots, lot_type, available, public_cap, active_reserved, current_hour, NP):
    # displays every parking lot with its public availability and active lecturer reservation

    # LOCAL DECLARATIONS
    # i, slot : int
    # period_name : string

    # ALGORITHM
    slot = GetTimeSlot(current_hour)
    if (slot == 0):
        period_name = "BEFORE LECTURES (Off-Peak)"
    elif (slot == 1):
        period_name = "LECTURE HOURS (08:00-13:00)"
    else:
        period_name = "AFTER LECTURES (Off-Peak)"

    print("\n================================================================================")
    print("ITB JATINANGOR PARKING | Time: " + str(current_hour) + ":00 | " + period_name)
    print("================================================================================")
    for i in range(NP):
        print("[" + str(i + 1) + "] " + lots[i] + " (" + lot_type[i] + ")"
              + " | Public Open: " + str(available[i]) + "/" + str(public_cap[i])
              + " | Lecturer Reserved: " + str(active_reserved[i]))
    print("================================================================================\n")
    return


# Function Definition: FindNearestParking
def FindNearestParking(target_idx, buildings, bld_x, bld_y, lots, lot_x, lot_y, available, NP):
    # starting from the chosen building, visits parking lots from closest to farthest (Euclidean
    # distance) until one has a free public slot; returns the lot index or -1 if none has space

    # LOCAL DECLARATIONS
    # visited : array [0..NP-1] of bool
    # i, step, visited_count, nearest_idx, found_idx : int
    # min_dist, dist : float

    # ALGORITHM
    visited = [False] * NP
    visited_count = 0
    found_idx = -1
    step = 1

    print("\n[INFO] Searching nearest parking from " + buildings[target_idx] + "...")

    while (visited_count < NP and found_idx == -1):
        nearest_idx = -1
        min_dist = 0.0

        # Find the closest unvisited lot (first candidate seeds min_dist; no magic big number)
        for i in range(NP):
            if (visited[i] == False):
                dist = CalculateDistance(bld_x[target_idx], bld_y[target_idx], lot_x[i], lot_y[i])
                if (nearest_idx == -1 or dist < min_dist):
                    min_dist = dist
                    nearest_idx = i

        visited[nearest_idx] = True
        visited_count = visited_count + 1
        print("  -> Step " + str(step) + ": Checking [" + str(nearest_idx + 1) + "] " + lots[nearest_idx]
              + " (Distance: " + str(round(min_dist, 2)) + " units) | Public Open: " + str(available[nearest_idx]))

        if (available[nearest_idx] > 0):
            found_idx = nearest_idx
        else:
            print("     Result: FULL. Continuing to next nearest...")
            step = step + 1

    return found_idx


# MAIN PROGRAM ALGORITHM

# DATASET
buildings = [
    "gerbang utama",  # [1]
    "Asrama dosen ITB Jatinangor",  # [2]
    "Sekretariat HMH 'Selva' ITB",  # [3]
    "Gedung SITH",  # [4]
    "Gedung SITH",  # [5]
    "Gedung SITH",  # [6]
    "Gedung Lab Kayu",  # [7]
    "Instalasi Pengolahan Sampah Terpadu ITB Jatinangor",  # [8]
    "GKU2",  # [9]
    "GKU1",  # [10]
    "gedung FTSL",  # [11]
    "Gedung SITH-Rekayasa",  # [12]
    "Gedung A",  # [13]
    "Gedung B",  # [14]
    "Gedung C",  # [15]
    "Gedung D",  # [16]
    "Gedung F",  # [17]
    "Mushola Al-Washat",  # [18]
    "Gedung Lab. Kriya",  # [19]
    "Gedung FTI",  # [20]
    "Lab. Kimia dan Komputer",  # [21]
    "Asrama ITB Jatinangor TB5",  # [22]
    "Water Treatment Plant (WTP)",  # [23]
    "Green House",  # [24]
    "Gedung Labtek TPSDA",  # [25]
    "Asrama ITB Jatinangor TB1",  # [26]
    "Asrama ITB Jatinangor TB2",  # [27]
    "Asrama ITB Jatinangor TB3",  # [28]
    "Asrama ITB Jatinangor TB4",  # [29]
    "Gelanggang Olah Raga (GOR) Jatinangor",  # [30]
    "Gedung Serba Guna (GSG)",  # [31]
    "Gedung Perpustakaan Pusat",  # [32]
    "Gedung Rektorat ITB Jatinangor",  # [33]
    "Gedung ITB - Korea Cyber Security R&D Center",  # [34]
    "Amphiteater",  # [35]
    "Lapangan Basket ITB Jatinangor",  # [36]
    "Lapangan Sepak Bola",  # [37]
    "Lab terpadu"   # [38]
]

bld_x = [13.0, 22.0, 22.0, 24.0, 24.0, 25.0, 17.0, 22.0, 16.0, 20.0, 13.0, 13.0, 17.0, 15.0, 18.0, 18.0, 17.0, 16.0, 15.5, 12.0, 13.0, 12.0, 8.0, 9.0, 12.0, 16.0, 15.0, 14.0, 13.0, 17.0, 19.0, 21.0, 22.0, 21.0, 16.0, 20.0, 12.0, 20.0]
bld_y = [0.0, 3.0, 6.5, 6.5, 5.0, 3.0, 7.0, 12.0, 13.5, 16.0, 16.0, 18.0, 21.0, 21.0, 20.0, 18.0, 17.0, 19.0, 19.5, 22.0, 21.0, 19.0, 25.0, 22.0, 15.0, 26.0, 25.0, 24.0, 23.0, 29.0, 26.0, 23.0, 20.0, 22.0, 23.0, 24.0, 30.0, 13.0]

lots = [
    "Parkiran Mobil Barat Gerbang Utama",  # [1]
    "Parkir Lab Gem",  # [2]
    "Parkir area Robot recycle ITB",  # [3]
    "parkiran Gedung FTSL",  # [4]
    "parkiran danau situ 1",  # [5]
    "Parkiran gedung SITH-R",  # [6]
    "Parkiran asrama TB5",  # [7]
    "Parkiran Barat Labtek II A",  # [8]
    "Parkiran Asrama TB 1 - 4",  # [9]
    "Parkiran Lapangan Bola ITB jatinangor",  # [10]
    "Parkiran GOR Futsal",  # [11]
    "Parkiran lapangan Basket ITB Jatinangor",  # [12]
    "Parkiran Selatan GKU 3",  # [13]
    "Parkiran Barat GKU 3",  # [14]
    "Parkiran Timur Gedung rektorat",  # [15]
    "Parkiran Barat Gedung rektorat",  # [16]
    "Parkiran Utama Lab terpadu",  # [17]
    "Parkiran Selatan Lab terpadu (2 parking space only)",  # [18]
    "Parkiran Barat IPST ITB Jatinangor",  # [19]
    "Parkiran gedung SITH (Labtek V A)",  # [20]
    "Parkiran Asrama Dosen"   # [21]
]

lot_type = ["C", "C", "C", "C and M", "C", "C and M", "C and M", "C", "C and M", "C", "C and M", "C", "C", "C", "C", "C and M", "C and M", "C", "C and M", "C", "C"]
lot_x = [12.0, 17.0, 16.0, 15.0, 12.0, 13.0, 12.0, 10.0, 14.0, 9.0, 19.0, 21.0, 22.0, 21.0, 23.0, 21.0, 20.0, 21.0, 21.0, 25.0, 22.0]
lot_y = [0.0, 6.0, 11.0, 14.0, 16.0, 17.0, 19.0, 22.0, 26.0, 30.0, 27.0, 26.0, 22.0, 23.0, 21.0, 19.0, 12.0, 13.0, 9.0, 6.0, 3.0]
capacity = [84, 20, 26, 32, 12, 31, 26, 30, 70, 25, 45, 23, 10, 10, 20, 12, 40, 2, 15, 110, 35]

NB = len(buildings)
NP = len(lots)

LECT_PCT = [0, 30, 0]   # % of lot capacity reserved: [00:00-07:59, 08:00-12:59 (lectures), 13:00-23:59]
lecturer_schedule = []
for i in range(NP):
    lecturer_schedule.append([0, 0, 0])
public_cap = [0] * NP
available = [0] * NP
active_reserved = [0] * NP

print("=== ITB JATINANGOR PARKING SIMULATION ===")

# STEP 1: read and validate the simulation hour (it decides the lecturer reservation)
current_hour = ReadWholeNumber("Enter simulation hour (0-23): ", 0, 23)

# STEP 2 + 3: reserve lecturer slots out of capacity, THEN randomize the public availability
BuildLecturerSchedule(lecturer_schedule, capacity, LECT_PCT, NP)
ApplyLecturerReservation(capacity, lecturer_schedule, active_reserved, public_cap, current_hour, NP)
InitAvailability(available, public_cap, NP)

# STEP 4: query loop
DisplayBuildings(buildings, NB)
running = True

while (running == True):
    DisplayParkingStatus(lots, lot_type, available, public_cap, active_reserved, current_hour, NP)

    target_no = ReadWholeNumber("Enter destination building number (1 to " + str(NB) + "): ", 1, NB)
    target_idx = target_no - 1

    nearest_idx = FindNearestParking(target_idx, buildings, bld_x, bld_y, lots, lot_x, lot_y, available, NP)

    if (nearest_idx != -1):
        dist = CalculateDistance(bld_x[target_idx], bld_y[target_idx], lot_x[nearest_idx], lot_y[nearest_idx])
        available[nearest_idx] = available[nearest_idx] - 1
        print("\n[RESULT] Destination: [" + str(target_no) + "] " + buildings[target_idx])
        print("Nearest parking: [" + str(nearest_idx + 1) + "] " + lots[nearest_idx] + " (" + lot_type[nearest_idx] + ")")
        print("Distance: " + str(round(dist, 2)) + " units")
        print("Vehicle parked. Remaining public spots there: " + str(available[nearest_idx]) + "\n")
    else:
        print("\n[ALERT - CAMPUS FULL] No public parking spots available anywhere on campus!")
        print("Please proceed to Entrance Gate Parking / Turnaround.\n")

    choice = input("Simulate another arriving vehicle? (y/n): ")
    if (choice != 'y' and choice != 'Y'):
        running = False

print("\nSimulation ended.")
