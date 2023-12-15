import time
matrix = [
    [0,0,0],
    [0,0,0]
]

def pm():
    print(matrix[0])
    print(matrix[1])
    print()
def rm():
    for i in range(2):
        for j in range(2):
            matrix[i][j] = 0



open('log.txt', 'w').close()
with open('log.txt', 'a') as f:
    f.write('Starting...\n')

log = open('log.txt','a', encoding="utf-8")

log.write('Starting...\n')
log.write('Matrix:\n')

time.sleep(5)
log.close()