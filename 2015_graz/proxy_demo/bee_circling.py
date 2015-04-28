#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A simple demo of bee-casu interaction
# Taken from assisi-python/casu_proxy_led example.

from assisipy import bee

if __name__ == '__main__':

    # Connect to the bee
    walker = bee.Bee(name='Bee-001')
    
    # Let the bee run in circles
    walker.set_vel(0.975, 1.2)
    


            

    
