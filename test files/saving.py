import subprocess
import sys
import pygame

pygame.init()
output = subprocess.run(
    [sys.executable, 'test files/saving2.py'],
    capture_output=True,
    text=True,
)
result = output.stdout

print(result)