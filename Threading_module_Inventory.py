#Will run as a base_point for the threading 
from update_Inventory_Threading import Update_Ebay_Inventory  
import pandas as pd
import threading
import math

INPUT_FILE_NAME = 'UploadAsins - Orginal.csv'
NUM_WORKERS = 10

total_line_count = len(pd.read_csv(INPUT_FILE_NAME)) / NUM_WORKERS
decimal,line_count_general = math.modf(total_line_count)		#general is all the lines given to workers, except the last one which will less than the rest e.g 100 / 3 = 33.33
ramining_lines = decimal * NUM_WORKERS 

def worker(num,line_count):
    Update_Ebay_Inventory(INPUT_FILE_NAME,int(num) + 1,int(line_count))
    return

threads = []
j = 0
for i in range(NUM_WORKERS):
	line_count = line_count_general
	t = threading.Thread(target=worker, args=(i,line_count))
	threads.append(t)
	t.start()
	j += 1

