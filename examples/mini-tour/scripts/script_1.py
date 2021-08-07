#
# This file is part of Brazil Data Cube Reproducible Research Management API.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube Reproducible Research Management CLI is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Example script."""

from emoji import emojize

#
# Introduction
#
print(emojize("Today we will eat together :pot_of_food:"))

#
# 1° step
#
print(emojize("1: Let's start with some fruits (:grapes: :melon: :watermelon:)"))
with open("data/file.txt", "w") as file:
    file.write("The first\n")
