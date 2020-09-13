import timeit
import asyncio
import time

def sort():
    start = timeit.default_timer()

    unSortedList = asyncio.run(getAllNumbersToSort())
    sortedList = mergeSort(unSortedList)
    writeOutFile(sortedList)
    stop = timeit.default_timer()
    execution_time = stop - start
    
    fp = open("async_time.txt", 'w')
    fp.write(str(execution_time) + " seconds")
    fp.close()
    print("Execution Time: " + str(execution_time))
    
async def getAllNumbersToSort():
    
    finalList = []
    
    result = await asyncio.gather(
        readInputFile("input/unsorted_1.txt"),
        readInputFile("input/unsorted_2.txt"),
        readInputFile("input/unsorted_3.txt"),
        readInputFile("input/unsorted_4.txt"),
        readInputFile("input/unsorted_5.txt"),
        readInputFile("input/unsorted_6.txt"),
        readInputFile("input/unsorted_7.txt"),
        readInputFile("input/unsorted_8.txt"),
        readInputFile("input/unsorted_9.txt"),
        readInputFile("input/unsorted_10.txt")
    )

    result = list(result)
    for unsortedList in result:
        finalList.extend(unsortedList)

    return finalList
    
async def readInputFile(inputFile):
    await asyncio.sleep(1)
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
    fp = open("async_sorted.txt", 'w')
    for num in sortedList:
        fp.write("%i\n" %num)
    fp.close()
        
sort()
