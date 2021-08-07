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
# 4° step
#
print(emojize("4: Now, repeat!!! (:taco: :bread: :grapes: :pot_of_food:)"))

with open("data/file2.txt", "r") as inp:
    with open("data/file3.txt", "r") as inp2:
        with open("data/file4.txt", "w") as out:
            out.writelines(inp.readlines())
            out.writelines(inp2.readlines())
            out.write("Second and third to generate the fourth\n")
