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
# 2° step
#
print(emojize("2: Now the bread (:bread: :bread: :bread:)"))

with open("data/file.txt", "r") as inp:
    with open("data/file2.txt", "w") as out:
        out.writelines(inp.readlines())
        out.write("The first and the second\n")
