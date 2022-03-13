import time
import smbus
import subprocess

def tempChanger(msb, lsb):                                    #msbを8bitずらしてlsbとつなげる
    mlsb = ((msb << 8) | lsb)
    return (-45 + 175 * int(str(mlsb), 10) / float(pow(2, 16) - 1))       #変換式にあてはめる



def humidChanger(msb, lsb):
    mlsb = ((msb << 8) | lsb)
    return (100 * int(str(mlsb), 10) / float(pow(2, 16) - 1))

i2c = smbus.SMBus(1)
i2c_addr = 0x44                                                                    #I2c用

i2c.write_byte_data(i2c_addr, 0x21, 0x30)
time.sleep(0.5)

while 1:
    i2c.write_byte_data(i2c_addr, 0xE0, 0x00)
    data = i2c.read_i2c_block_data(i2c_addr, 0x00, 6)
#値確認用
    print( str('{:.6g}'.format(tempChanger(data[0], data[1]))) + "C" )
    print( str('{:.6g}'.format(humidChanger(data[3], data[4]))) + "%" )
    print("------")
#書き込み動作
    f = open('out.csv', 'w', encoding='UTF-8')
    f.write(str(tempChanger(data[0], data[1]))+'\n')
    f.write(',')
    f.write(str(humidChanger(data[3], data[4]))+'\n')
    f.close()
    cmd = "mosquitto_pub --host an1.icgw.ntt.com --port 1883 --debug --qos 0 --topic s/us -f out.csv --id-prefix client" #1値のみ: --message '&s'  % (tempChanger(data[0], data[1]))
    proc = subprocess.run(cmd, shell = True)
    cmd = "mosquitto_pub --host an1.icgw.ntt.com --port 1883 --debug --qos 0 --topic s/uc/templateMorita02 -f out.csv --id-prefix client" #1値のみ: --message '&s'  % (tempChanger(data[0], data[1]))
    proc = subprocess.run(cmd, shell = True)
    time.sleep(10)