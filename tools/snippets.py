textsurface = self.myfont.render('Some Text', False, (0, 0, 0))
self.screen.blit(textsurface, (0, 0))


for pix in b_pix:  # TODO haengt programm auf! berechnung zu langsam

    # verkuerzt die rechenzeit(nur in bereich ueberpruefen)
    if car.position.x+200 < pix[0] < car.position.x+200 and car.position.y+200 < pix[1] < car.position.y+200:
        r_q = np.array(pix)
        dist = np.cross(a_vec, (r_q - r_1_vec)) / np.linalg.norm(a_vec)
        # print(f'distance:{dist}')

    if dist < smallest_dist:
        sm_dist_pix = r_q
