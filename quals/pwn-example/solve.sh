#!/bin/bash
(sleep 1; base64 -w0 solve.elf; echo ) | nc chall.polygl0ts.ch 12020
