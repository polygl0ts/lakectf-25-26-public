Solve:
1. Download the song
2. See there's two artworks

first flag part

1. One is really big, bigger than the original one
2. Download the original one on soundcloud
3. It's far smaller
4. xor the pixels (jpeg introduces noise that's expected)
5. morse appears -> .-- ...-- .-.. .-.. ..--.- .---- ..--.- .... ----- .--. ...-- ..--.-
6. first part: w3ll_1_h0p3_ (lowercases)


second flag part

1. One has a longer name than it should (the artist one)
2. (It's weird there's more songs than artists, but the id of the avatar is longer...)
3. Look at the image on Soundcloud
4. https://i1.sndcdn.com/avatars-Bk0PQeRYuTMEc8pH-yiwoNQ-t200x200.jpg
5. Not the same url
6. 2CoZeyWPDmofN5AakwuSymP6jojz32XmjA6oavj base58 
7. decode and xor Bk0PQeRYuTMEc8pH-yiwoNQ
8. second part: 7h47_y0u_l1k3d_7h3_50ng!!!!!



END: assemble flag in `EPFL{}` -> `EPFL{w3ll_1_h0p3_7h47_y0u_l1k3d_7h3_50ng!!!!!}`

Note: the original artist has been contacted and agreed that this challenge use her song
