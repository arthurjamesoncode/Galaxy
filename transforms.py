def transform(self, x, y):
    lin_y = y * self.perspective_point_y / self.height

    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y
    
    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y

    proportion_y = diff_y / self.perspective_point_y
    proportion_y = proportion_y * proportion_y

    diff_y = self.perspective_point_y * proportion_y
    
    tr_y = self.perspective_point_y - diff_y
    tr_x = self.perspective_point_x + diff_x * proportion_y

    return int(tr_x), int(tr_y)