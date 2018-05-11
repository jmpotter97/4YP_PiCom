import imageio as io

img = io.imread('cat2_out 4PAM 2018-05-11 15:04.jpg',pilmode='RGB')
io.imwrite('out1.jpg',img[:,:,0])
io.imwrite('out2.jpg',img[:,:,1])
io.imwrite('out1.jpg',img[:,:,2])
