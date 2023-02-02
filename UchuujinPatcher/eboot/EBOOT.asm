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


//CGS 2892_02 info
//XY texture
.org 0x08946978
	.dh 0, 0			//BGM Volume
	.dh 92, 0           //SE Volume
	.dh 0, 14           //Voice Volume
	.dh 0, 0            //-
	.dh 0, 0            //-
	.dh 0, 0            //-
	.dh 70, 28          //Message Spee
	.dh 0, 42           //Message Auto
	.dh 0, 0            //-
	.dh 0, 28           //Voices
	.dh 0, 0            //-
	.dh 0, 0            //-
	.dh 0, 0            //-
	.dh 98, 14          //System SE Sounds
	.dh 0, 56           //Message Skip
	.dh 102, 56         //-
	.dh 0, 70           //Install Data
	.dh 102, 70         //-
	.dh 0, 224          //min
	.dh 26, 224         //max
	.dh 0, 42           //-
	.dh 0, 42           //-
	.dh 0, 42           //-
	.dh 0, 42           //-
	.dh 0, 196          //On
	.dh 24, 196         //Off
	.dh 48, 196         //Custom
	.dh 48, 210         //-
	.dh 0, 210          //-
	.dh 24, 210         //No
	.dh 48, 210         //Install Only
	.dh 96, 210         //Force Skip
	.dh 96, 196         //Low
	.dh 120, 196        //Mid
	.dh 144, 196        //Fast

//renderWidth,renderHeight,textureWidth,textureHeight
.org 0x089449E0
	.dh 92,14,92,14				//BGM Volume
	.dh 80,14,80,14             //SE Volume
	.dh 98,14,98,14             //Voice Volume
	.dh 0,14,0,14               //-
	.dh 0,14,0,14               //-
	.dh 0,14,0,14               //-
	.dh 100,14,100,14           //Message Speed
	.dh 136,14,136,14           //Message Auto Speed
	.dh 0,14,0,14               //-
	.dh 70,14,70,14             //Voices
	.dh 0,14,0,14               //-
	.dh 0,14,0,14               //-
	.dh 0,14,0,14               //-
	.dh 128,14,128,14           //System SE Sound
	.dh 102,14,102,14           //Message Skip
	.dh 62,14,62,14             //-
	.dh 102,14,102,14           //Install Data
	.dh 70,14,70,14             //-
	.dh 26,12,26,12             //min
	.dh 30,12,30,12             //max
	.dh 0, 0, 0, 0				//-
	.dh 0, 0, 0, 0              //-
	.dh 0, 0, 0, 0              //-
	.dh 0, 0, 0, 0              //-
	.dh 24, 14, 24, 14          //On
	.dh 24, 14, 24, 14          //Off
	.dh 48, 14, 48, 14          //Custom
	.dh 112, 14, 112, 14        //-
	.dh 48, 14, 48, 14          //-
	.dh 24, 14, 24, 14          //No
	.dh 48, 14, 48, 14          //Install Only
	.dh 60, 14, 60, 14          //Force Skip
	.dh 24, 14, 24, 14          //Low
	.dh 24, 14, 24, 14          //Mid
	.dh 24, 14, 24, 14          //Fast
	.dh 24, 14, 24, 14 			//Instant Only
//BG width
.org 0x0894B908
				.dh 88			//BGM Volume
				.dh 76          //SE Volume
				.dh 94          //Voice Volume
				.dh 124         //Message Speed
				.dh 66          //Message Auto Speed
				.dh 96          //Voices
				.dh 132         //System SE Sound
				.dh 98          //Message Skip
				.dh 98          //Install Data
.org 0x894b84e
				.dh 32			//Low
.org 0x894b85a 	
				.dh 32			//Mid
.org 0x894b866 	
				.dh 32			//Fast
.org 0x894b872 	
				.dh 32			//Instant
.org 0x894b87e 	
				.dh 32			//On
.org 0x894b88a 	
				.dh 32			//Off
.org 0x894b896 	
				.dh 48			//Custom
.org 0x894b8ae 	
				.dh 32			//No
.org 0x894b8ba 	
				.dh 48			//Instant Only
.org 0x894b8c6 	
				.dh 60			//Force Skip
.org 0x894b8de 	
				.dh 32			//Off Install Data
.org 0x894b8ea 	
				.dh 32			//On Install Data
//CGS 2892_02 info end






//CGS 2892_03 info
//X,Y,W,unk texture
.org 0x894b988
	//MOD						//ORIG
	.dh 0, 0, 32, 0				//.dh 0, 0, 24, 0			  //Nano
	.dh 0, 14, 43, 0            //.dh 0, 14, 36, 0            //Hakase
	.dh 0, 28, 60, 0            //.dh 0, 28, 48, 0            //Sakamoto
	.dh 0, 42, 37, 0            //.dh 0, 42, 34, 0            //Yukko
	.dh 0, 56, 24, 0            //.dh 0, 56, 24, 0            //Mio
	.dh 0, 70, 24, 0            //.dh 0, 70, 24, 0            //Mai
	.dh 0, 84, 42, 0            //.dh 0, 84, 34, 0            //Misato
	.dh 0, 98, 50, 0            //.dh 0, 98, 58, 0            //Weboshi
	.dh 0, 112, 46, 0           //.dh 0, 112, 66, 0           //Fecchan
	.dh 0, 126, 54, 0           //.dh 0, 126, 24, 0           //Sasahara
	.dh 64, 0, 35, 0            //.dh 66, 0, 24, 0            //Daiku
	.dh 64, 14, 56, 0           //.dh 66, 14, 24, 0           //Sekiguchi
	.dh 64, 28, 93, 0           //.dh 66, 28, 36, 0           //Sakurai Makoto
	.dh 64, 42, 64, 0           //.dh 66, 42, 36, 0           //Nakanojou
	.dh 64, 56, 45, 0           //.dh 66, 56, 24, 0           //Annaka
	.dh 64, 70, 43, 0           //.dh 66, 70, 24, 0           //Tanaka
	.dh 64, 84, 52, 0           //.dh 66, 84, 48, 0           //Principal
	.dh 64, 98, 78, 0           //.dh 66, 98, 48, 0           //Vice Principal
	.dh 64, 112, 91, 0          //.dh 66, 112, 48, 0          //Takasaki-Sensei
	.dh 64, 126, 85, 0          //.dh 66, 126, 48, 0          //Sakurai-Sensei
	.dh 160, 0, 80, 0           //.dh 114, 0, 48, 0           //Mr.Nakamura
	.dh 160, 14, 35, 0          //.dh 114, 14, 36, 0          //Sister
	.dh 160, 28, 61, 0          //.dh 114, 28, 24, 0          //Tamamura
	.dh 160, 42, 44, 0          //.dh 114, 42, 34, 0          //Kiyoshi
	.dh 160, 56, 62, 0          //.dh 114, 56, 78, 0          //Gentleman
	.dh 160, 70, 83, 0          //.dh 114, 70, 60, 0          //Mr.Nakanojou
	.dh 160, 84, 32, 0          //.dh 114, 84, 34, 0          //Itako
	.dh 160, 98, 48, 0          //.dh 114, 98, 46, 0          //Soldiers
	.dh 160, 112, 83, 0         //.dh 114, 112, 58, 0         //Princess Starla
	.dh 160, 140, 69, 0         //.dh 114, 140, 44, 0         //Dialogue SE
	.dh 160, 126, 40, 0         //.dh 114, 126, 36, 0         //Others

//BG width
.org 0x0894B948
	//mod	//orig
	.dh 40	//.dh 32			//Nano
	.dh 51	//.dh 44           //Hakase
	.dh 68	//.dh 56           //Sakamoto
	.dh 45	//.dh 42           //Yukko
	.dh 32	//.dh 32           //Mio
	.dh 32	//.dh 32           //Mai
	.dh 50	//.dh 42           //Misato
	.dh 58	//.dh 66           //Weboshi
	.dh 54	//.dh 74           //Fecchan
	.dh 62	//.dh 32           //Sasahara
	.dh 43	//.dh 32           //Daiku
	.dh 64	//.dh 32           //Sekiguchi
	.dh 101	//.dh 44           //Sakurai Makoto
	.dh 72	//.dh 44           //Nakanojou
	.dh 53	//.dh 32           //Annaka
	.dh 51	//.dh 32           //Tanaka
	.dh 60	//.dh 56           //Principal
	.dh 86	//.dh 56           //Vice Principal
	.dh 99	//.dh 56           //Takasaki-Sensei
	.dh 93	//.dh 56           //Sakurai-Sensei
	.dh 88	//.dh 56           //Mr. Nakamura
	.dh 43	//.dh 44           //Sister
	.dh 69	//.dh 32           //Tamamura
	.dh 52	//.dh 42           //Kiyoshi
	.dh 70	//.dh 86           //Gentleman
	.dh 91	//.dh 68           //Mr.Nakanojou
	.dh 40	//.dh 42           //Itako
	.dh 56	//.dh 54           //Soldiers
	.dh 91	//.dh 66           //Princess Starla
	.dh 77	//.dh 52           //Dialogue SE
	.dh 48	//.dh 44           //Others

//CGS 2892_03 info end
.close