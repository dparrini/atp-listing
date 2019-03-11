"""
MIT License

Copyright (c) 2019 David Rodrigues Parrini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


ATP LIS FILE FORMAT UTILITIES
"""
import re


# Statistical output variables regular expressions
__RE_STAT_OUT_V = "^Statistical output of  node  voltage"
__RE_STAT_OUT_C = "^Statistical output of branch current"
__RE_STAT_OUT_E = "^Statistical output of branch energy "
__RE_STAT_OUT_PEAK = "^      Peak extremum of subset has value "
__RE_STAT_OUT_SHOT = "(?i)^      simulation ([0-9 ]{1,3})  for the variable \
having names  \"([A-Z][A-Z0-9_\- ]{5})\"  and  \
\"(([A-Z][A-Z0-9_\- ]{5})| {6})\"."

# LIS simulation data
__RE_SIMULATION_DATETIME = " Date (dd-mth-yy) and time of day (hh.mm.ss) = ([0-9 ]{1,2})-([a-zA-Z]+)-([0-9]{2}18)  ([0-9]{2}):([0-9]{2}):([0-9]{2})   "
__RE_SOURCE_DATE = "Source code date is ([0-9 ]{1,2}) ([a-zA-Z]+) ([0-9]{4})\."

# LIS file parts
RE_PART_INPUT_CARDS_BEGIN = re.compile("^Descriptive interpretation of input data cards.")
RE_PART_INPUT_CARDS_END   = re.compile("^$")

RE_PART_NODE_CONNECTIONS_BEGIN = re.compile("^List of input elements that are connected to each node.")
RE_PART_NODE_CONNECTIONS_END   = re.compile("^--------------\+------------------------------")

RE_PART_PHASOR_SOLUTION_UNKNOWN_VOLT_BEGIN = re.compile("^Sinusoidal steady-state phasor solution, branch by branch.")
RE_PART_PHASOR_SOLUTION_UNKNOWN_VOLT_END   = re.compile("^(?=     Total network loss)")

RE_PART_PHASOR_SOLUTION_SWITCH_BEGIN = re.compile("^Output for steady-state phasor switch currents.")
RE_PART_PHASOR_SOLUTION_SWITCH_END   = re.compile("^$")

RE_PART_PHASOR_SOLUTION_KNOWN_VOLT_BEGIN = re.compile("^Solution at nodes with known voltage.")
RE_PART_PHASOR_SOLUTION_KNOWN_VOLT_END   = re.compile("^(?=  ---- Initial flux of coil)")

RE_PART_OUTPUT_VARIABLES_BEGIN = re.compile("^Column headings for the ([0-9 ]+) EMTP output variables follow.")
RE_PART_OUTPUT_VARIABLES_END   = re.compile("^Blank card terminating all plot cards.")

RE_PART_STATISTICAL_SIMULATIONS_BEGIN = re.compile("^The data case now ready to be solved is a statistical overvoltage study")
RE_PART_STATISTICAL_SIMULATIONS_END = re.compile("^(?= MAIN20 dumps OVER12 dice seed)")

RE_PART_STATISTICAL_RESULTS_BEGIN = re.compile("^MODTAB, AINCR, XMAXMX")
RE_PART_STATISTICAL_RESULTS_END   = re.compile("^(?= .... Questionable Kolmogorov-Smirnov test result)")

__re_stat_out_v = re.compile(__RE_STAT_OUT_V)
__re_stat_out_c = re.compile(__RE_STAT_OUT_C)
__re_stat_out_e = re.compile(__RE_STAT_OUT_E)
__re_stat_out_peak = re.compile(__RE_STAT_OUT_PEAK)
__re_stat_out_shot = re.compile(__RE_STAT_OUT_SHOT)

__re_simulation_datetime = re.compile(__RE_SIMULATION_DATETIME)
__re_source_date = re.compile(__RE_SOURCE_DATE)


# Statistical distribution tables regular expressions
__RE_V_CAPTION_STR = "(?i)^Statistical distribution of peak voltage \
at node  \"([A-Z][A-Z0-9_\- ]{0,4}(A|B|C) {0,4})\""

__RE_C_CAPTION_STR = "(?i)^Statistical distribution of peak current  \
for branch  \"([A-Z][A-Z0-9_\- ]{0,4}(A|B|C) {0,4})\"  to  \
\"([A-Z][A-Z0-9_\- ]{0,4}(A|B|C) {0,4})\""

__RE_E_CAPTION_STR = "(?i)^Statistical distribution of peak energy   \
for branch  \"([A-Z][A-Z0-9_\- ]{0,4}(A|B|C) {0,4})\"  to  \
\"([A-Z][A-Z0-9_\- ]{0,4}(A|B|C) {0,4})\"."

__RE_TABLE_ENDING = "(?i)^Summary of preceding table follows:"

__RE_RANDOM_SW_TIMES = "^             Random switching times for simulation number"

__RE_T183_SW_TIMES = "^CLOSING INSTANTS \[SECONDS\]"


__re_v_caption = re.compile(__RE_V_CAPTION_STR)
__re_c_caption = re.compile(__RE_C_CAPTION_STR)
__re_e_caption = re.compile(__RE_E_CAPTION_STR)
__re_table_ending = re.compile(__RE_TABLE_ENDING)

_re_random_sw_times = re.compile(__RE_RANDOM_SW_TIMES)
_re_t183_sw_times = re.compile(__RE_T183_SW_TIMES)


class LisSwitchingTimes:
    """Base class for extraction of statistical simulations switching time."""
    def __init__(self, lisfile):
        # A, B, and C phases switching times
        self.sw_a = []
        self.sw_b = []
        self.sw_c = []

        self.read(lisfile)

    def read(self, lisfile):
        pass


class ThreePhaseSwitchingTimes(LisSwitchingTimes):
    """Extract all switching times written in the lis file after "Random switching 
    times for simulation number: x"
    Works only with one threephase statistical switch.
    """
    def read(self, lisfile):
        with open(lisfile, "r") as file:
            line = file.readline()
            while line != "":
                if _re_random_sw_times.match(line):
                    """
                    Random switching times for simulation number  XXX:
                     23  XXXXXXXXXXXXX   24  XXXXXXXXXXXXX   25  XXXXXXXXXXXXX
                    """
                    # read next line with timings
                    line = file.readline()
                    self.sw_a.append(float(line[38:51]))
                    self.sw_b.append(float(line[58:71]))
                    self.sw_c.append(float(line[78:91]))

                line = file.readline()


class StatTable(object):
    """
    Base class for reading statistical distribution table data of an ATP .lis 
    file.
    """
    def __init__(self):
        self.type  = ""
        self.node1 = ""
        self.node2 = ""
        self.table = []
        self.base  = 1.0
        self.gmean = 0.0
        self.gvar  = 0.0
        self.gstd  = 0.0
        self.umean = 0.0
        self.uvar  = 0.0
        self.ustd  = 0.0
        self.BASE_COLUMN = 0

    def read_base(self, line):
        """
        Given the first line of a voltage/current distribution table, read its
        base.
        """
        self.base = float(line[self.BASE_COLUMN:].strip())

    def read_phase_table(self, file, line):
        # read voltage/current base at first table line 
        self.read_base(line)
        # skip next two rows
        file.readline()
        file.readline()
        # read data
        self.read_table(file)

    def read_summary_table(self, file, line):
        # skip summary of c phase table
        for i in range(4): file.readline()
        # skip "SUMMARY   SUMMARY..."
        for i in range(7): file.readline()
        # read data
        self.read_table(file)

    def open_and_read(self, lisfile, summary):
        with open(lisfile, "r") as file:
            self.read(file, summary)

    def read(self, file, summary):
        pass

    def read_table(self, file):
        # read summary table data
        line = file.readline()
        while not is_table_ending(line):
            self.table.append(stat_table_read_line(line))
            line = file.readline()
        # table ending found, read mean, variance and std.
        meanl = file.readline()
        varl  = file.readline()
        stdl  = file.readline()

        gu_data = stat_table_read_ending_data(meanl + varl + stdl)
        self.gmean = gu_data[0]
        self.gvar  = gu_data[1]
        self.gstd  = gu_data[2]
        self.umean = gu_data[3]
        self.uvar  = gu_data[4]
        self.ustd  = gu_data[5]

    def read_v_table(self, lisfile, node, summary = False):
        self.node1 = node
        self.node2 = ""
        self.type = "voltage"

        node_prefix = _get_node_name_prefix(node)

        # control for summary extraction
        phase = ""
        waitingTableEnd = False
        
        with open(lisfile, "r") as file:
            line = file.readline()
            while line != "":
                if is_vpeak_statistical_table(node_prefix, line) and not summary:
                    # get base
                    self.base = float(line[114:].strip())
                    # skip next two rows
                    file.readline()
                    file.readline()
                    # read data
                    self.read_table(file)
                    break

                elif summary:
                    if is_vpeak_statistical_table(node_prefix, line):
                        # get base
                        self.base = float(line[114:].strip())
                        if phase == "":
                            phase = "A"
                        elif phase == "A":
                            phase = "B"
                        elif phase == "B":
                            waitingTableEnd = True

                    if waitingTableEnd and is_table_ending(line):
                        # reset
                        phase = ""
                        waitingTableEnd = False
                        # skip summary of c phase table
                        for i in range(4): file.readline()
                        # skip "SUMMARY   SUMMARY..."
                        for i in range(7): file.readline()
                        # read data
                        self.read_table(file)
                        break

                line = file.readline()

    def read_c_table(self, lisfile, node1, node2, summary = False):
        self.node1 = node1
        self.node2 = node2
        self.type = "current"

        node1_prefix = _get_node_name_prefix(node1)
        node2_prefix = _get_node_name_prefix(node2)

        # control for summary extraction
        phase = ""
        waitingTableEnd = False

        with open(lisfile, "r") as file:
            line = file.readline()
            while line != "":
                if is_cpeak_statistical_table(node1_prefix, node2_prefix, line) and not summary:
                    # get base current
                    self.base = float(line[116:].strip())
                    # skip next two rows
                    file.readline()
                    file.readline()
                    # read data
                    self.read_table(file)
                    break

                elif summary:
                    if is_cpeak_statistical_table(node1_prefix, node2_prefix, line):
                        # get base
                        self.base = float(line[116:].strip())
                        if phase == "":
                            phase = "A"
                        elif phase == "A":
                            phase = "B"
                        elif phase == "B":
                            waitingTableEnd = True

                    if waitingTableEnd and is_table_ending(line):
                        # reset
                        phase = ""
                        waitingTableEnd = False
                        # skip summary of c phase table
                        for i in range(4): file.readline()
                        # skip "SUMMARY   SUMMARY..."
                        for i in range(7): file.readline()
                        # read data
                        self.read_table(file)
                        break

                line = file.readline()


class VoltageStatTable(StatTable):
    """
    Read data from statistical distribution of peak voltages tables of an ATP
    .lis file, given its node name and whether its the summary table or not.
    """
    def __init__(self, lisfile, node, summary = False):
        super(VoltageStatTable, self).__init__()
        self.node1 = node
        self.node2 = ""
        self.type = "voltage"
        self.BASE_COLUMN = 114
        self.open_and_read(lisfile, summary)

    def read(self, file, summary):
        node_prefix = _get_node_name_prefix(self.node1)
        line = file.readline()
        if not summary:
            while line != "":
                if is_vpeak_statistical_table(node_prefix, line):
                    self.read_phase_table(file, line)
                    break
                line = file.readline()
        else:
            # control for summary extraction (after C phase)
            phase = ""
            waitingTableEnd = False
            while line != "":
                if is_vpeak_statistical_table(node_prefix, line):
                    # get base
                    self.read_base(line)
                    if phase == "":
                        phase = "A"
                    elif phase == "A":
                        phase = "B"
                    elif phase == "B":
                        waitingTableEnd = True

                if waitingTableEnd and is_table_ending(line):
                    # reset
                    phase = ""
                    waitingTableEnd = False
                    self.read_summary_table(file, line)
                    break

                line = file.readline()


class CurrentStatTable(StatTable):
    """
    Read data from statistical distribution of peak current tables of an ATP
    .lis file, given its branch nodes names and whether its the summary table 
    or not.
    """
    def __init__(self, lisfile, node1, node2, summary = False):
        super(CurrentStatTable, self).__init__()
        self.node1 = node1
        self.node2 = node2
        self.type = "current"
        self.BASE_COLUMN = 116
        self.open_and_read(lisfile, summary)

    def read(self, file, summary):
        node_prefix1 = _get_node_name_prefix(self.node1)
        node_prefix2 = _get_node_name_prefix(self.node2)
        line = file.readline()
        if not summary:
            while line != "":
                if is_cpeak_statistical_table(node_prefix1, node_prefix2, line):
                    self.read_phase_table(file, line)
                    break
                line = file.readline()
        else:
            # control for summary extraction (after C phase)
            phase = ""
            waitingTableEnd = False
            while line != "":
                if is_cpeak_statistical_table(node_prefix1, node_prefix2, line):
                    # get base
                    self.read_base(line)
                    if phase == "":
                        phase = "A"
                    elif phase == "A":
                        phase = "B"
                    elif phase == "B":
                        waitingTableEnd = True

                if waitingTableEnd and is_table_ending(line):
                    # reset
                    phase = ""
                    waitingTableEnd = False
                    self.read_summary_table(file, line)
                    break

                line = file.readline()


def get_shots_information(lisfile):
    shots = []
    with open(lisfile, "r") as file:
        line = file.readline()
        while line != "":
            vmatch = __re_stat_out_v.match(line)
            cmatch = __re_stat_out_c.match(line)
            ematch = __re_stat_out_e.match(line)

            if vmatch:
                # peak value
                line = file.readline()
                if __re_stat_out_peak.match(line):
                    peak = float(line[40:55].strip())
                    line = file.readline()
                    smatch = __re_stat_out_shot.match(line)
                    ttype = "Tensão"

                    no01, no02, shot = get_shot_information(line)
                    shots.append([ttype, no01, no02, peak, shot])

            elif cmatch:
                # peak value
                line = file.readline()
                if __re_stat_out_peak.match(line):
                    peak = float(line[40:55].strip())
                    line = file.readline()
                    smatch = __re_stat_out_shot.match(line)
                    ttype = "Corrente"

                    no01, no02, shot = get_shot_information(line)
                    shots.append([ttype, no01, no02, peak, shot])

            elif ematch:
                # peak value
                line = file.readline()
                if __re_stat_out_peak.match(line):
                    peak = float(line[40:55].strip())
                    line = file.readline()
                    smatch = __re_stat_out_shot.match(line)
                    ttype = "Energia"

                    no01, no02, shot = get_shot_information(line)
                    shots.append([ttype, no01, no02, peak, shot])

            line = file.readline()

    return shots


def get_shot_information(line):
    smatch = __re_stat_out_shot.match(line)
    shot = int(smatch.group(1).strip())
    no01 = smatch.group(2)
    no02 = smatch.group(4)

    if not no02:
        no02 = ""

    return no01, no02, shot


def get_statistical_variable_names(lisfile):
    tables = []
    with open(lisfile, "r") as file:
        for line in file:
            vmatch = __re_v_caption.match(line)
            cmatch = __re_c_caption.match(line)
            ematch = __re_e_caption.match(line)
            
            if vmatch:
                tno01 = vmatch.group(1)
                tno02 = ""
                ttype = "Tensão"
                tables.append([ttype, tno01, tno02])

            elif cmatch:
                tno01 = cmatch.group(1)
                tno02 = cmatch.group(3)
                ttype = "Corrente"
                tables.append([ttype, tno01, tno02])

            elif ematch:
                tno01 = ematch.group(1)
                tno02 = ematch.group(3)
                ttype = "Energia"
                tables.append([ttype, tno01, tno02])

    return tables


def stat_table_read_line(line_str):
    """
    Extract statistical distribution table values given one of its lines.
    Returns a list containing its values in the same sequence, units and types
    as in .lis file.
    """
    interval    =   int(line_str[ 0:10])
    voltage_pu  = float(line_str[10:30])
    voltage_v   = float(line_str[30:50])
    frequency_d =   int(line_str[50:64])
    frequency_c =   int(line_str[64:78])
    pu_ge_val   = float(line_str[78:98])

    return [interval, voltage_pu, voltage_v, frequency_d, frequency_c, pu_ge_val]


def _get_node_name_prefix(node_name):
    """
    Returns the node name prefix, without phase character or trailing 
    whitespaces.
    """
    wows_name = node_name.strip()
    return wows_name[:-1]


def __make_threephase_node_name(node_name_prefix, phase):
    """
    Returns a node name with "phase" sufix and trailing whitespaces (6 
    characters).
    """
    new_name = node_name_prefix + phase
    whitespaces = 6 - len(new_name)
    new_name = new_name + (" " * whitespaces)

    return new_name


def is_vpeak_statistical_table(node_name_prefix, line):
    """
    Given a node name prefix (without A, B or C phase sufix), checks a .lis line 
    whether its is the beginning of a statistical voltage distribution table.
    """
    node_names = [
        __make_threephase_node_name(node_name_prefix, "A"),
        __make_threephase_node_name(node_name_prefix, "B"),
        __make_threephase_node_name(node_name_prefix, "C")
    ]
    matchobj = __re_v_caption.match(line)

    return matchobj and matchobj.group(1) in node_names


def is_cpeak_statistical_table(node1_name_prefix, node2_name_prefix, line):
    """
    Given two node name prefixes (without A, B or C phase sufix), checks a .lis line 
    whether its is the beginning of a statistical voltage distribution table.
    """
    node1_names = [
        __make_threephase_node_name(node1_name_prefix, "A"),
        __make_threephase_node_name(node1_name_prefix, "B"),
        __make_threephase_node_name(node1_name_prefix, "C")
    ]
    node2_names = [
        __make_threephase_node_name(node2_name_prefix, "A"),
        __make_threephase_node_name(node2_name_prefix, "B"),
        __make_threephase_node_name(node2_name_prefix, "C")
    ]
    matchobj = __re_c_caption.match(line)

    return matchobj and matchobj.group(1) in node1_names and matchobj.group(3) in node2_names


def is_table_ending(line):
    """Test if the current line is the table ending line."""
    return __re_table_ending.match(line) is not None


def stat_table_read_ending_data(ending_lines):
    """
    Given the last three lines of a statistical distribution table (after
    "Summary of preceding table follows" line), returns the grouped data mean,
    variance, standard deviation and ungrouped data mean, variance and standard
    deviation.
    """
    GROUPED_DATA_START = 40
    GROUPED_DATA_END   = 54
    UNGROUP_DATA_START = 59
    UNGROUP_DATA_END   = 73

    lines = ending_lines.splitlines()
    mean_line = lines[0]
    var_line  = lines[1]
    std_line  = lines[2]

    group_mean = float(mean_line[GROUPED_DATA_START : GROUPED_DATA_END])
    group_var  = float( var_line[GROUPED_DATA_START : GROUPED_DATA_END])
    group_std  = float( std_line[GROUPED_DATA_START : GROUPED_DATA_END])

    ungroup_mean = float(mean_line[UNGROUP_DATA_START : UNGROUP_DATA_END])
    ungroup_var  = float( var_line[UNGROUP_DATA_START : UNGROUP_DATA_END])
    ungroup_std  = float( std_line[UNGROUP_DATA_START : UNGROUP_DATA_END])

    return (group_mean,   group_var,   group_std, 
            ungroup_mean, ungroup_var, ungroup_std)


class LisFile(object):
    input_cards_lines = []
    node_connections_lines = []
    
    phasor_solution_uvolt_lines = []
    phasor_solution_kvolt_lines = []
    phasor_solution_switches_lines = []

    output_variables_lines = []

    stat_simulation_lines = []
    stat_result_lines = []

    def __init__(self):
        pass

    def load(self, file):
        with open(file, "r") as f:
            where = None
            for line in f:
                # test each line to check in which block it is
                if RE_PART_INPUT_CARDS_BEGIN.match(line):
                    where = "INPUT"
                if RE_PART_INPUT_CARDS_END.match(line):
                    where = None

                if RE_PART_STATISTICAL_SIMULATIONS_BEGIN.match(line):
                    where = "STAT_SIM"
                if RE_PART_STATISTICAL_SIMULATIONS_END.match(line):
                    where = None

                if RE_PART_STATISTICAL_RESULTS_BEGIN.match(line):
                    where = "STAT_RES"
                if RE_PART_STATISTICAL_RESULTS_END.match(line):
                    where = None

                # append lines when inside a data block
                if where == "INPUT":
                    self.input_cards_lines.append(line)
                if where == "STAT_SIM":
                    self.stat_simulation_lines.append(line)
                if where == "STAT_RES":
                    self.stat_result_lines.append(line)

        print("Input cards")
        print(self.input_cards_lines)
        print()
        print("Statistical simulations")
        print(self.stat_simulation_lines)
        print()
        print("Statistical results")
        print(self.stat_result_lines)
        print()

        self._process_input_cards()

    def _process_input_cards(self):
        self.input_cards = []
        for line in self.input_cards_lines:
            vertbar = line.index("|")
            fline = line[vertbar+1:]
            self.input_cards.append(fline)





if __name__ == "__main__":
    print( "Testing making node names:")
    print( " ", __make_threephase_node_name("U500", "A"))
    print( " ", __make_threephase_node_name("U", "A"))
    print( " ", __make_threephase_node_name("ABCDE", "A"))

    print( "Testing class (voltage table)")
    file = "./ex/03_st_entr5f_4b6t_xg_c.lis"
    x = StatTable()
    x.read_v_table(file, "TRPYDB", False)
    print( "  Ungrouped mean:", x.umean)
    x = VoltageStatTable(file, "TRPYDB", False)
    print( "  Ungrouped mean:", x.umean)

    print( "Testing class (current table)")
    x = StatTable()
    x.read_c_table(file, "XGU50A", "TRPYDA", False)
    print( "  Ungrouped mean:", x.umean)
    x = CurrentStatTable(file, "XGU50A", "TRPYDA", False)
    print( "  Ungrouped mean:", x.umean)

    print( "Testing class (current table summary)")
    x = StatTable()
    x.read_c_table(file, "XGU50A", "TRPYDA", True)
    print( "  Ungrouped mean:", x.umean)
    x = CurrentStatTable(file, "XGU50A", "TRPYDA", True)
    print( "  Ungrouped mean:", x.umean)

    print( "Testing class (voltage table summary)")
    x = StatTable()
    x.read_v_table(file, "TRPYDB", True)
    print( "  Ungrouped mean:", x.umean)
    x = VoltageStatTable(file, "TRPYDB", True)
    print( "  Ungrouped mean:", x.umean)

    print (get_statistical_variable_names(file))
    print (get_shots_information(file))

    # test overall file reading
    l = LisFile()
    l.load(file)


