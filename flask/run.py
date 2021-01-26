# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app import app, db

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
