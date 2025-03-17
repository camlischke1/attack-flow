import os
import json
from collections import defaultdict
from tabulate import tabulate


class TTPSequencer():
    '''
        This class ingests a directory of Attack Flow files and creates tactic adjacency lists for all tactics and for a "filtered" subset of tactics
    '''
    def __init__(self, path):
        self.filters = [
                        "TA0043",
                        "TA0042",
                        "TA0002",
                        "TA0005",
                        "TA0011",
                        "TA0010"
                        ]
        self.adj_matrix,self.filtered_adj_matrix,self.freq_dict = self.load_adjacency_matrices(path)

        self.tabulate_matrix(self.filtered_adj_matrix)
        self.tabulate_matrix(self.adj_matrix)


    def load_adjacency_matrices(self, path):
        '''
            Reads through a given directory of .AFB files and calculates the transitions from tactic to tactic.
        '''
        if not os.path.isdir(path):
            raise ValueError(f"The given path {path} is not a directory.")
        
        adjacency_list = defaultdict(lambda: defaultdict(int))
        filtered_adjacency_list = defaultdict(lambda: defaultdict(int))
        frequency_dict = {}

        for filename in os.listdir(path):
            # for all files with the .afb extension

            if filename.endswith('.afb'):
                file_path = os.path.join(path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)

                prev_tactic = None
                prev_filtered_tactic = None

                # find the Tactic ID for "action" objects
                for obj in data['objects']:
                    if obj.get("template") == "action":
                        properties = obj.get("properties")
                        for property in properties:
                            # extract the tactic ID
                            if property[0] == 'tactic_id' and property[1] is not None and "TA" in property[1]:
                                curr_tactic = property[1]

                                # build the frequency list
                                if curr_tactic in frequency_dict:
                                    frequency_dict[curr_tactic] += 1
                                else:
                                    frequency_dict[curr_tactic] = 1

                                # build the adjacency list if there is a previous tactic that is different from the current tactic
                                if prev_tactic is not None and prev_tactic != curr_tactic:
                                    adjacency_list[prev_tactic][curr_tactic] += 1
                                prev_tactic = curr_tactic 
                                    
                                # build the filtered adjacency list if the current tactic is not filtered and is different from previous tactic
                                if curr_tactic not in self.filters:
                                    if prev_filtered_tactic is not None and prev_filtered_tactic != curr_tactic:
                                        filtered_adjacency_list[prev_filtered_tactic][curr_tactic] += 1
                                        prev_filtered_tactic = curr_tactic
                                    prev_filtered_tactic = curr_tactic

        return adjacency_list,filtered_adjacency_list,frequency_dict
    


    def tabulate_matrix(self,data:defaultdict):
        '''
            Function reads in a dictionary and tabulates the adjacency matrix.
            The cells read "<row> tactic transitioned to <column> tactic <cell> number of times." 
        '''
        column_keys = set()
        for sub_dict in data.values():
            column_keys.update(sub_dict.keys())

        # Sort column keys for consistent ordering
        column_keys = sorted(column_keys)

        # Prepare the table data
        table_data = []
        for row_key, sub_dict in sorted(data.items()):
            row = [f"From {row_key}"] + [sub_dict[col_key] for col_key in column_keys]
            table_data.append(row)

        print(tabulate(table_data, headers= ['Transitioned to'] + column_keys, tablefmt='pretty'))


if __name__ == '__main__':
    path = os.path.join(os.getcwd(),"corpus")
    sequencer = TTPSequencer(path)