# Import LCD library
from RPLCD import i2c
# Import sleep library
from time import sleep
# Import config parser
import configparser
# Import tenacity if something goes wrong
#from tenacity import retry
#from tenacity.wait import wait_fixed
# Import requests
import requests
import RPi.GPIO as GPIO

def btn_callback(pin):
    global host
    sleep(0.03)
    if GPIO.input(pin):
        if pin == 15:
            # cat
            toggle_cat(host, True)
        if pin == 13:
            # home
            toggle_cat(host, False)
            go_home(host)

def go_home(host):
    try:
        x = requests.post('http://'+host+'/ad/php/set_band_len.php', data = {'band': 'home'}, timeout = (2, 5))
    except requests.exceptions.RequestException as e:
        return 'ERR'

def toggle_cat(host, mode):
    global cat_sta
    cat_sta = not cat_sta
    #print('cat: on' if cat_sta else 'cat: off')
    if mode:
        try:
            x = requests.post('http://'+host+'/ad/php/enable_disable_cat.php', data = {'cat_status': 'true' if cat_sta else 'false'}, timeout = (2, 5))
        except requests.exceptions.RequestException as e:
            return 'ERR'
    else: 
        try:
            x = requests.post('http://'+host+'/ad/php/enable_disable_cat.php', data = {'cat_status': 'false'}, timeout = (2, 5))
        except requests.exceptions.RequestException as e:
            return 'ERR'


def init_lcd():
    # constants to initialise the LCD
    lcdmode = 'i2c'
    cols = 20
    rows = 4
    charmap = 'A02'
    i2c_expander = 'PCF8574'
    # Generally 27 is the address. Find yours using: i2cdetect -y 1 
    address = 0x27 
    port = 1 # 0 on an older Raspberry Pi

    # Initialise the LCD
    lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap, cols=cols, rows=rows)
    cat = (0b00100,
	    0b00010,
	    0b11111,
	    0b00110,
	    0b01100,
	    0b11111,
	    0b01000,
	    0b00100,
        )
    nocat = (0b00000,
	    0b10001,
	    0b01010,
	    0b00100,
	    0b01010,
	    0b10001,
	    0b00000,
	    0b00000,
        )
    home = (0b11111,
	    0b10101,
	    0b10101,
	    0b10001,
	    0b10101,
	    0b10101,
	    0b11111,
	    0b00000,)
    lcd.create_char(0, cat)
    lcd.create_char(1, nocat)
    lcd.create_char(2, home)

    return lcd

def read_cat_frequency(host):
    try:
        x = requests.post('http://'+host+'/ad/php/get_cat_frequency.php', timeout = (2, 5)).text
    except requests.exceptions.RequestException as e:
        return 'ERR'
    if x != '0':
        return x[0:-3]+'.'+x[-3:-2]
    else:
        return '/'

def read_cat_status(host):
    try:
        x = requests.get('http://'+host+'/ad/php/read_cat_status.php', timeout = (2, 5)).text
    except requests.exceptions.RequestException as e:
        return 'ERR'
    if x == '0': return '\x00'
    else: return '\x01'

def read_cat_on(host):
    global cat_sta
    try:
        x = requests.get('http://'+host+'/ad/php/read_cat_on.php', timeout = (2, 5)).text
    except requests.exceptions.RequestException as e:
        return 'ERR'
    if x == '1': 
        cat_sta = True
        return '\x00'
    else:
        cat_sta = False
        return '\x01'

def read_current_band(host):
    try:
        x = requests.get('http://'+host+'/ad/php/get_current_band.php', timeout = (2, 5)).text
    except requests.exceptions.RequestException as e:
        return 'ERR'
    return x.split(';')[0] 

def read_current_freq(host):
    try:
        x = requests.get('http://'+host+'/ad/php/read_current_freq.php', timeout = (2, 5)).text
    except requests.exceptions.RequestException as e:
        return 'ERR'
    return x

def read_485_status(host):
    try:
        x = requests.get('http://'+host+'/ad/php/get_485_status.php', timeout = (2, 5)).text
    except requests.exceptions.RequestException as e:
        return 'ERR'
    return x

def read_current_len(host):
    try:
        x = requests.post('http://'+host+'/ad/php/get_current_lengths.php', timeout = (2, 5)).text
    except requests.exceptions.RequestException as e:
        return 'ERR'
    return x.split(';')

def read_target_len(host):
    try:
        x = requests.post('http://'+host+'/ad/php/get_target_lengths.php', timeout = (2, 5)).text
    except requests.exceptions.RequestException as e:
        return 'ERR'
    return x.split(';')

def update_lcd(host, lcd):
    cf = read_cat_frequency(host)
    if cf != 'ERR':
        lcd.cursor_pos = (0, 0)
        lcd.write_string(cf.rjust(7))
        lcd.write(29)

        band = read_current_band(host)
        if band == 'home': 
            band = '  \x02'
            cf = '/'
        elif band:
            band = band.rjust(3)
            cf = read_current_freq(host)
        elif not band:
            band = '  \x01'
            cf = '/'
        lcd.cursor_pos = (0, 17)
        lcd.write_string(band)
        lcd.cursor_pos = (0,8)
        lcd.write_string(cf.rjust(5) + 'kHz')
        lcd.cursor_pos = (1, 0)
        lcd.write_string('CAT: '+read_cat_status(host)+' Controlled: '+read_cat_on(host))
        lcd.cursor_pos = (2, 0)
        cl = read_current_len(host)
        tl = read_target_len(host)
        lcd.write_string('Drv: ' + cl[0].rjust(5) + 'm ')
        lcd.cursor_pos = (3, 0)
        lcd.write_string('Ref: ' + cl[1].rjust(5) + 'm ')
        st485 = read_485_status(host)
        if st485 != 'ERR':
            if int(st485) > 0:
                lcd.cursor_pos = (2, 12)
                if tl[0] != cl[0]:
                    lcd.write(199)
                    lcd.write_string(' ' + tl[0].rjust(5) + 'm')
                else:
                    lcd.write_string('        ')
                lcd.cursor_pos = (3, 12)
                if tl[1] != cl[1]:
                    lcd.write(199)
                    lcd.write_string(' ' + tl[1].rjust(5) + 'm')
                else:
                    lcd.write_string('        ')
            else:
                lcd.cursor_pos = (2, 12)
                lcd.write_string('485 ERR!')
                lcd.cursor_pos = (3, 12)
                lcd.write_string('========')
    else:
        lcd.clear()
        lcd.cursor_pos = (1, 1)
        lcd.write_string('Connection Error!')
    sleep(0.7)

def test_lcd(lcd):
    for i in range(1, 254):
        lcd.cursor_pos = (0, 0)
        lcd.write_string(str(i).rjust(3) + ' ')
        lcd.write(i)
        sleep(1)

#@retry(wait=wait_fixed(10))
def main(host, lcd):
    global cat_sta
    cat_sta = False
    btn_cat = 15
    btn_hme = 13
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    GPIO.setup(btn_cat, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
    GPIO.setup(btn_hme, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
    GPIO.add_event_detect(btn_cat, GPIO.RISING, callback = btn_callback, bouncetime = 300) # Setup event on pin 10 rising edge
    GPIO.add_event_detect(btn_hme, GPIO.RISING, callback = btn_callback, bouncetime = 300) # Setup event on pin 10 rising edge

    while True:
        update_lcd(host, lcd)
        #test_lcd(lcd)

    GPIO.cleanup() # Clean up

global host
if __name__ == '__main__':
    config = configparser.ConfigParser()
    #config.read('/etc/remotedisplay')
    host = '192.168.1.30'
    lcd = init_lcd()
    lcd.backlight_enabled = True
    lcd.clear()
    #main(config['DEFAULT']['Host'], lcd)
    main(host, lcd)
    # Clear the LCD screen
    lcd.close(clear = True)
