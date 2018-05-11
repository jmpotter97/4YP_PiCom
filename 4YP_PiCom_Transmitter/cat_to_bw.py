import imageio as io

img = io.imread('cat2.jpg', pilmode = 'L')
io.imwrite('cat2_bw.jpg', img)
