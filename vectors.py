import math

# This contains the code needed for Vector2 stuff.
# Decided to make my own program here because I prefer working with my own things and not fighting with Pygame or wxpython's code.
class Vector2:
    ## Supports things from various extensions if possible.
    def __init__(self, x: float|int|list|tuple = None, y: float|int = None):
        
        self.x: float|int = 0.0
        self.y: float|int = 0.0
        
        
        if x == None:
            pass
        elif isinstance(x,Vector2):
            self.x = x.x
            self.y = x.y
        elif isinstance(x,list) or isinstance(x,tuple):
            self.x = x[0]
            self.y = x[1]
        elif isinstance(x,float) or isinstance(x,int):
            self.x = x

            if y == None:
                self.y = x
            else:
                self.y = y
        
        # Support for imported programs.
        else:
            # wx.Size
            try:
                from wx import Size # Import the specific class here.

                # Perform calculations here.
                if isinstance(x,Size):
                    self.x = x.GetWidth()
                    self.y = x.GetHeight()
            except ModuleNotFoundError: # try and except allows this to work if the import is not present.
                pass
                
            # wx.Point
            try:
                from wx import Point
                if isinstance(x,Point):
                    self.x = x.x
                    self.y = x.y
            
            except ModuleNotFoundError:
                pass
    
    def __trunc__(self):
        return Vector2(math.trunc(self.x), math.trunc(self.y))
    
    def __round__(self, v=None):
        if v:
            return Vector2(round(self.x,v), round(self.y,v))
        else:
            return Vector2(round(self.x), round(self.y))
    
    def __abs__(self):
        return Vector2(abs(self.x), abs(self.y))
    
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    

    def __add__(self, value):
        value_vec = Vector2(value)
        return Vector2(
            self.x + value_vec.x,
            self.y + value_vec.y
        )

    def __sub__(self, value):
        value_vec = Vector2(value)
        return Vector2(
            self.x - value_vec.x,
            self.y - value_vec.y
        )

    def __mul__(self, value):
        value_vec = Vector2(value)
        return Vector2(
            self.x * value_vec.x,
            self.y * value_vec.y
        )

    def __truediv__(self, value):
        value_vec = Vector2(value)
        return Vector2(
            self.x / value_vec.x,
            self.y / value_vec.y
        )

    def __mod__(self, value):
        value_vec = Vector2(value)
        return Vector2(
            self.x % value_vec.x,
            self.y % value_vec.y
        )

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __repr__(self):
        return "Vector2(" + str(self.x) + ", " + str(self.y) + ")"

    def __bool__(self):
        if self.x != 0 and self.y != 0:
            return True
        else:
            return False
    
    def __eq__(self, value):
        value_vec = Vector2(value)
        if self.x == value_vec.x and self.y == value_vec.y:
            return True
        else:
            return False
    
    def __ne__(self, value):
        value_vec = Vector2(value)
        if self.x != value_vec.x and self.y != value_vec.y:
            return True
        else:
            return False
    
    def __lt__(self, value):
        value_vec = Vector2(value)
        if self.x < value_vec.x or self.y < value_vec.y:
            return True
        else:
            return False

    def __gt__(self, value):
        value_vec = Vector2(value)
        if self.x > value_vec.x or self.y > value_vec.y:
            return True
        else:
            return False
    
    def __ge__(self, value):
        value_vec = Vector2(value)
        if self.x >= value_vec.x or self.y >= value_vec.y:
            return True
        else:
            return False

    def min(self, value):
        value_vec = Vector2(value)
        result = Vector2(
            min(self.x, value_vec.x),
            min(self.y, value_vec.y)
        )
        return result

    def max(self, value):
        value_vec = Vector2(value)
        result = Vector2(
            max(self.x, value_vec.x),
            max(self.y, value_vec.y)
        )
        return result

    def clamp(self, min, max):
        min_vec = Vector2(min)
        max_vec = Vector2(max)
        
        result = Vector2(
            max(max_vec.x, min(self.x, min_vec.x)),
            max(max_vec.y, min(self.y, min_vec.y))
        )
        return result
    
    # Returns a copy of itself as a Tuple.
    def get_as_tuple(self): return (self.x, self.y)

    # Returns a copy of itself with x and y rounded into integer values.
    def get_as_Vector2i(self): return round(self)

    # Returns a copy of itself as wx.Point. Requires wxPython installed.
    def get_as_wxPoint(self):
        try:
            import wx
            self_int = self.get_as_Vector2i()
            return wx.Point(self_int.x, self_int.y)
        
        except ModuleNotFoundError:
            # Error handling if the required module isn't installed.
            print("Function get_as_wxPoint requires the wxPython Module installed.")
    
    # Returns a copy of itself as wx.Size. Requires wxPython installed.
    def get_as_wxSize(self):
        try:
            import wx
            self_int = self.get_as_Vector2i()
            return wx.Size(self_int.x, self_int.y)

        except ModuleNotFoundError:
            # Error handling if the required module isn't installed.
            print("Function get_as_wxSize requires the wxPython Module installed.")

    # Returns a copy of itself as pygame.Vector2. Requires Pygame installed.
    def get_as_pgVector2(self):
        try:
            import pygame
            return pygame.Vector2(self.x, self.y)

        except ModuleNotFoundError:
            # Error handling if the required module isn't installed.
            print("Function get_as_pgVector2 requires the pygame Module installed.")

if __name__ == "__main__":
    print(abs(Vector2((1, 3))))