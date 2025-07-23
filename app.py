
from flask import Flask, request, make_response, jsonify, Response, send_from_directory
import base64
import datetime
import requests
import csv
import os
import sys
import json

app = app(__name__, static_folder='.')

@app.route('/giphy_carol-burnett-maid-over-it-3ohzdUuqOMFwxPyUvu664783anp2NDd2em42MXVweml2dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw3ohzdUuqOMFwxPyUvu76-gif')
def redirect():
    return send_from_directory('.', 'redirect.html')

@app.route('/giphy_SkyTV-homer-simpson-simpsons-hiding-2A3DG83664783anp2NDd2em42MXVwjfh6784GHGFjkfdkfheml2dCZlcD12MV9pbnRlcm5hbF9yvN8uaBiaNR-gif')
def redirect2():
    return send_from_directory('.', 'redirect2.html')

@app.route('/pudgypenguins-fire-burning-on-ZhS9PL4HQO6o9s9G83664783anp2NDd2em42MXVwe64783anhjfHlksdjf5682dFG099jjjhrGGF647893456GFGgghjp2NDd2e6ce-gif')
def redirect3():
    return send_from_directory('.', 'redirect3.html')

@app.route('/star-wars-han-solo-rHR8qPw3ohzdUuqUvu664783anpOMFwx1mC5m42MXVweml8377759fhhpoebfghjk8906GHghSqzjbcn543GHdkbxbHG2dCZlcD1O6o9s9G836V3G-gif')
def redirect4():
    return send_from_directory('.', 'redirect4.html')


if __name__ == '__main__':
    app.run(debug=True)
