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
# 3° step
#
print(emojize("3: Tacos and burritos!!! (:taco: :burrito:)"))

with open("data/file2.txt", "r") as inp:
    with open("data/file3.txt", "w") as out:
        out.writelines(inp.readlines())
        out.write("Read the second and generate a new file\n")
