import imageio as io

img = io.imread('cat.png', pilmode = 'L')
io.imwrite('cat_bw.png', img)
