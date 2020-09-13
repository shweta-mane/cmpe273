import timeit
import time

def sort():
    start = timeit.default_timer()
    unSortedList = getAllNumbersToSort()
    sortedList = mergeSort(unSortedList)
    writeOutFile(sortedList)
    stop = timeit.default_timer()
    execution_time = stop - start

    fp = open("time.txt", 'w')
    fp.write(str(execution_time) + " seconds")
    fp.close()
    print("Execution Time: " + str(execution_time))

def getAllNumbersToSort():
    finalList = []
    for fileNum in range (1, 11):
        inputFile = "input/unsorted_" + str(fileNum) + ".txt"
        numbers = readInputFile(inputFile)
        finalList = finalList + numbers
    return finalList

def readInputFile(inputFile):
    time.sleep(1)
    fp = open(inputFile, 'r')
    numbers = fp.read().strip().split('\n')
    fp.close()
    numbers = [int(num) for num in numbers]
    return numbers

def mergeSort(unSortedList):
    n = len(unSortedList)
    if(n == 1):
        return unSortedList

    list1 = []
    for i in range(0, int(n/2)):
        list1.append(unSortedList[i])

    list2 = []
    for j in range(int(n/2), n):
        list2.append(unSortedList[j])

    list1 = mergeSort(list1)
    list2 = mergeSort(list2)

    return merge(list1, list2)

def merge(list1, list2):
    len1 = len(list1)
    len2 = len(list2)
    mergedList = []

    i = 0
    j = 0

    while i < len1 and j < len2:
        if(list1[i] < list2[j]):
            mergedList.append(list1[i])
            i += 1
        else:
            mergedList.append(list2[j])
            j +=1

    while(i < len1):
        mergedList.append(list1[i])
        i += 1
    while(j < len2):
        mergedList.append(list2[j])
        j += 1

    return mergedList

def writeOutFile(sortedList):
    fp = open("sorted.txt", 'w')
    for num in sortedList:
        fp.write("%i\n" %num)
    fp.close()
        
sort()

