program lbl_input
implicit none

integer   lev,prof,lev1
parameter (lev=55,prof=50,lev1=55)!1039
real*4    p(lev,prof),t(lev,prof),ozo(lev,prof),wv(lev,prof)
real*4    p1(lev1,prof),t1(lev1,prof),ozo1(lev1,prof),wv1(lev1,prof)
real*4    tem(prof,lev),H2O(prof,lev),o3(prof,lev)
real*4    tra2(lev1,4),trah2(lev1,4),tra(lev,4),trah(lev,4)
integer   i,j,iprof,jj,kk,iii,jjj,iadd
real*4    angle,va(6),height(lev),pp(lev),tsurf(prof),scant(7)
real*4    blank(lev),bwn,ewn
real*4    maxwn,bwn0,ewn0
character*3 lay(54)
CHARACTER CXID*52
character(len=20) :: bwn_str
character*4 :: c2
character*1 :: c1

data lay/'001','002','003','004','005','006','007','008','009','010','011','012','013','014','015','016','017','018','019','020',&
'021','022','023','024','025','026','027','028','029','030','031','032','033','034','035','036','037','038','039','040',&
'041','042','043','044','045','046','047','048','049','050','051','052','053','054'/!,'055','056','057','058','059','060',&
!'061','062','063','064','065','066','067','068','069','070','071','072','073','074','075','076','077','078','079','080',&
!'081','082','083','084','085','086','087','088','089','090','091','092','093','094','095','096','097','098','099','100'/
data scant/2.58,2.94,3.72,4.83,6.1,7.2,9/



open(11,file='./profile/pressure.txt',form='formatted')
do i=1,lev
   read(11,*) p1(i,:)
end do
close(11)
do i=1,lev
   p(i,:)=p1(lev+1-i,:)
end do



open(12,file='./profile/temperature.txt',form='formatted')
do i=1,lev
   read(12,*) t1(i,:)
end do
close(12)
do i=1,lev
   t(i,:)=t1(lev+1-i,:)
end do



open(13,file='./profile/ozo_test_1573.txt',form='formatted')
do i=1,lev
   read(13,*) ozo1(i,:)
end do
close(13)
do i=1,lev
   ozo(i,:)=ozo1(lev+1-i,:)
end do


open(14,file='./profile/wv.txt',form='formatted')
do i=1,lev
   read(14,*) wv1(i,:)
end do
close(14)
do i=1,lev
   wv(i,:)=wv1(lev+1-i,:)
end do




do i=1,6
angle=1+0.25*(i-1)
va(i)=acos(1./angle)
va(i)=va(i)*180./3.1415927
enddo 

  
height=0.00
blank=0.00




do iprof=1,prof
tsurf(iprof)=t(1,iprof)
end do

!%%%%% for fixed gas
maxwn=1000.000
bwn0=6500.000
ewn0=8500.000
do iadd=0,0
bwn=bwn0+iadd*maxwn
ewn=ewn0+iadd*maxwn
!bwn=14500.000
!ewn=16500.000
!bwn=16500.000
!ewn=18500.000
!bwn=18500.000
!ewn=20500.000
!bwn=20500.000
!ewn=22500.000
!bwn=22500.000
!ewn=24500.000
!bwn=24500.000
!ewn=26500.000
!bwn=26500.000
!ewn=28500.000
!bwn=28500.000
!ewn=30500.000


do jj=1,1!angle
write( c1,'(i1)' ) jj
do iprof=1,50!prof
write( c2,'(i4)' ) iprof
open(44,file='TAPE5',status='REPLACE')
CXID='83P 55level profile to creat transmittance database'
write(44,"(A1,A52)") '$',CXID
write(44,"(1X,'HI=',I1,1X,'F4=',I1,1X,'CN=',I1,1X,'AE=',I1,1X,'EM=',I1,1X,'SC=',I1,1X,'FI=',I1,1X,'PL=',I1,1X,'TS=',I1,1X,'AM=',I1,1X,'MG=',I1,1X,'LA=',I1,1X,'OD=',I1,1X,'XS=',I1,3X,I1,I1,3X,I1,I1)") 1,1,1,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0!lbl的设置参数，笔记上有
write(44,"(2F10.3,60X,'REJ=',I1,5X,E10.3)") bwn,ewn,0,0.1!开始、结束波数和分辨率
!write(44,"(2F10.3,20X,F10.3)") tsurf(iprof),1.0000,0.0000！地表参数（经常出问题）
write(44,"(7I5,I2,1X,I2,2F10.3)")0,2,-55,1,1,7,1,0,0,0.0000,0.0000!层数、气体数量，最后两个是透过率和辐射率（？）
write(44,"(3F10.3)") p(55,iprof),p(1,iprof),180.000!0.00,1009.00,180.000!-va(jj)！最大最小气压值，和角度，180就是天顶角
write(44,"(8F10.3)") p(:,iprof)
write(44,"(I5,9X,3A8)")-55,'INPUT FOR CAMEX'!这里跟上面的两个层数要一致
do i=1,lev
WRITE(44,"(3F10.3,5X,A2,1X,A1,1X,7A)") height(i),p(i,iprof),t(i,iprof),'AA','L','AAAAAAA'!'AAAAAAAAAAAAAAAAAAAAAA'!这里开几个气体写几个A
!WRITE(44,"(8E15.8)") wv(i,iprof),blank(i),ozo(i,iprof),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i)
WRITE(44,"(8E15.8)") wv(i,iprof),blank(i),blank(i),blank(i),blank(i),blank(i),blank(i)
!WRITE(44,"(8E15.8)") wv(i,iprof),tra(i,1),ozo(i,iprof),blank(i),blank(i),blank(i),blank(i)!,blank(i),blank(i),blank(i),blank(i),blank(i),tra(i,10),blank(i),blank(i),tra(i,11)!这里开几个气体跟上面的A保持一致，不用的气体就blank
end do

!惰性气体
!WRITE(44,"(3I5)") 4,0,0
!WRITE(44,"(4A10)") 'CCL4','CFC11','CFC12','CFC14'  
!WRITE(44,"(I5,I5,A50)") 101,1,'CAMEX Wallops'
!do i=1,lev
!write(44,"(F10.3,5X,A4)") p(i),'AAAA'
!write(44,"(4E10.3)") trah(i,:)
!write(44,"(4E10.3)") blank(i),blank(i),blank(i),blank(i)
!write(44,"(4E10.3)") trah(i,:)
!end do

!这一部分不用管
write(44,"(F4.1)") -1.
                  
write(44,"(A1,1X,A30)") '$','Transfer to ASCII plotting data'
write(44,"(1X,'HI=',I1,1X,'F4=',I1,1X,'CN=',I1,1X,'AE=',I1,1X,'EM=',I1,1X,'SC=',I1,1X,'FI=',I1,1X,'PL=',I1,1X,'TS=',I1,1X,'AM=',I1,1X,'MG=',I1,1X,'LA=',I1,1X,'OD=',I1,1X,'XS=',I1,3X,I1,3X,I1)") 0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0
WRITE(44,"(A1,1X,19A)")'#','Plot title not used'
write(44,"(4F10.4,4I5,F10.3,I2,I3,I5)") bwn,ewn,10.2000,100.000,5,0,12,0,1.0000,0,0,0
write(44,"(2F10.4,2F10.3,6I5,I2,3X,I2,I3)") 0.0000,1.2000,7.0200,0.2000,4,0,1,1,0,0,0,3,27
write(44,"(4F10.4,4I5,F10.3,I2,I3,I5)") bwn,ewn,10.2000,100.000,5,0,12,0,1.0000,0,0,0
write(44,"(2F10.4,2F10.3,6I5,I2,3X,I2,I3)") 0.0000,1.2000,7.0200,0.2000,4,0,1,1,0,0,0,3,28
write(44,"(F4.1)") -1.
write(44,"(A5)") '%%%%%'


! call system('./script_run_example.pl')
! write(bwn_str, '(F9.3)') bwn
! call system('mv ODint_001 ./OD001save_H2O/ODint_001-'//trim(adjustl(bwn_str)))

!call system('mv TAPE12_test test_'//trim(adjustl(c2))//'P_angel'//trim(adjustl(c1))//'_dt ')
!call system('mv test_'//trim(adjustl(c2))//'P_angel'//trim(adjustl(c1))//'_dt ./lblrtm_transmittance_both_1/')!tape12
!do kk=1,54!lay
!call system('mv ODint_'//lay(kk)//' test_'//trim(adjustl(c2))//'P_angel'//trim(adjustl(c1))//'_od_'//lay(kk)//'')
!call system('mv test_'//trim(adjustl(c2))//'P_angel'//trim(adjustl(c1))//'_od_'//lay(kk)//' ./lblrtm_od_and_others/')!001第一层(layer)，1P第一个profile，od光学厚度，即tape11

!end do
close(44)
end do
end do
end do

end program lbl_input
