.PSP

.open "work/isofiles/EBOOT_DEC.BIN","work/isofiles/EBOOT_patched.BIN",0x8804000 -0xc0

//textbox line limit char
.org 0x8804d28
	li	a0,0x29
	
//speaker y pos
.org 0x8807d04
	addiu	a1,a2,0xC0

.org 0x8807db8
	addiu	a0,a0,0x12

//text y pos
.org 0x8809788
	addiu	a0,a0,0xD0

.org 0x88098c8
	nop	
.org 0x88098e8
	addiu	a0,a0,0x15
.org 0x88098f4
	addiu	a0,a1,0x12



//log textbox line limit char
.org 0x8813b58
	li	a2,0x29
	
	
	
//other limit
.org 0x08804F54
	li	a2,0x29
.org 0x08807374
	li	a2,0x29
.org 0x08813770
	li	a2,0x29
.org 0x08807434
	li	a2,0x29
.org 0x088070E8
	
	
	
//checksum always true
.org 0x883b644
	li	v0,0x1
	
	
.org 0x884e154
	jal	vwf_speaker
	

.org 0x884e158
	nop	
.org 0x884e160
	nop	
.org 0x884e7ec
	nop	
.org 0x884e7f4
	nop	
.org 0x884e804
	addu	a2,a2,a1


.org 0x884e820
	jal	vwf_text
	
	
	

.org 0x896e514
.func vwf_text
	li	v0,0x5C
	mult	s1,v0
	mflo	a0
	addu	v0,a0,a1
	lbu	v0,0x5B(v0)//load width from lt.bin
	lbu	a0,0x5EB0(s5)
	beq	a0,zero,Lab1
	move	a0,v0
	lhu	a0,0x5ED0(s5)
	addu	a2,a2,a0
	addu	a0,a0,v0
Lab1:   
	sh	a0,0x5ED0(s5)
	jr	ra
	move	a0,s1
.endfunction	



.func vwf_speaker
	li	v0,0x5C
	mult	a0,v0
	mflo	a0
	addu	v0,a0,a1
	lbu	v0,0x5B(v0)//load width from lt.bin
	beq	s3,zero,Lab2
	move	a0,v0
	lhu	a0,0x30(s5)
	addu	a2,a2,a0
	addu	a0,a0,v0
Lab2: 
	sh	a0,0x30(s5)
	jr	ra
	lhu	a0,0x0(s0)
.endfunction	

.close