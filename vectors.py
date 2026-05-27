import math
import wx

class Vector2:
    def __init__(self, x: float|int|list|tuple|wx.Point|wx.Size = None, y: float|int = None):
        
        self.x: float|int = 0.0
        self.y: float|int = 0.0
        
        if x == None:
            pass
        elif isinstance(x,wx.Size):
            self.x = x.GetWidth()
            self.y = x.GetHeight()
        elif isinstance(x,Vector2) or isinstance(x,wx.Point):
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
    
    def __trunc__(self):
        return Vector2(math.trunc(self.x), math.trunc(self.y))
    
    def __round__(self, v):
        return Vector2(round(self.x,v), round(self.y,v))
    
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
    
    def get_tuple(self): return (self.x, self.y)
    def get_Vector2i(self): return Vector2(int(self.x),int(self.y))

class Rect2:
    def __init__(self, x: float|int|list|tuple|Vector2 = None, y: float|int|list|tuple|Vector2 = None, w: float|int = None, h: float|int = None):
        self.position: Vector2 = Vector2()
        self.size: Vector2 = Vector2()

        if x == None:
            pass
        elif isinstance(x,float) or isinstance(x,int):
            self.position = Vector2(x,y)
            self.size = Vector2(w,h)
        elif isinstance(x,Vector2):
            self.position = x
            self.size = y
        elif isinstance(x,list) or isinstance(x,tuple):
            self.position = Vector2(x)

if __name__ == "__main__":
    print(abs(Vector2((1, 3))))