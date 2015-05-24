import numpy

__all__ = ['extractObservation']


powsof2 = (1, 2, 4, 8, 16, 32, 64, 128,
                         256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072)

def decode(estate):
    """
    decodes the encoded state estate, which is a string of 61 chars
    """
#    powsof2 = (1, 2, 4, 8, 16, 32, 64, 128)
    dstate = numpy.empty(shape = (22, 22), dtype = numpy.int)
    for i in range(22):
        for j in range(22):
            dstate[i, j] = 2
    row = 0
    col = 0
    totalBitsDecoded = 0
    reqSize = 31
    assert len(estate) == reqSize, "Error in data size given %d! Required: %d \n data: %s " % (len(estate), reqSize, estate)
    check_sum = 0
    for i in range(len(estate)):
        cur_char = estate[i]
        if (ord(cur_char) != 0):
            check_sum += ord(cur_char)
        for j in range(16):
            totalBitsDecoded += 1
            if (col > 21):
                row += 1
                col = 0
            if ((int(powsof2[j]) & int(ord(cur_char))) != 0):
                dstate[row, col] = 1
            else:
                dstate[row, col] = 0
            col += 1
            if (totalBitsDecoded == 484):
                break
    print "totalBitsDecoded = ", totalBitsDecoded
    return dstate, check_sum;


def extractObservation(data):
    """
     parse the array of strings and return array 22 by 22 of doubles
    """

    obsLength = 487
    levelScene = numpy.empty(shape = (22, 22), dtype = numpy.int)
    enemiesFloats = []
    dummy = 0
    if(data[0] == 'E'):
        mayMarioJump = (data[1] == '1')
        isMarioOnGround = (data[2] == '1')
        levelScene, check_sum_got = decode(data[3:34])
        check_sum_recv = int(data[34:])
        if check_sum_got != check_sum_recv:
            print "Error check_sum! got %d != recv %d" % (check_sum_got, check_sum_recv)

        return (mayMarioJump, isMarioOnGround, levelScene)
    data = data.split(' ')
    if (data[0] == 'FIT'):
        status = int(data[1])
        distance = float(data[2])
        timeLeft = int(data[3])
        marioMode = int(data[4])
        coins = int(data[5])
        
        return status, distance, timeLeft, marioMode, coins

    elif(data[0] == 'O'):
        mayMarioJump = (data[1] == 'true')
        isMarioOnGround = (data[2] == 'true')
        k = 0
        for i in range(22):
            for j in range(22):
                levelScene[i, j] = int(data[k + 3])
                k += 1
        k += 3
        marioFloats = (float(data[k]), float(data[k + 1]))
        k += 2        
        while k < len(data):
            enemiesFloats.append(float(data[k]))
            k += 1
        
        return (mayMarioJump, isMarioOnGround, marioFloats, enemiesFloats, levelScene, dummy)

    else:
        raise "Wrong format or corrupted observation..."
