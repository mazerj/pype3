
EDU>> x=x./p2mGetPPD(pf);
EDU>> 
EDU>> y=y./p2mGetPPD(pf);
EDU>> subplot(3,1,1);plot(t/1000, x, 'r', t/1000, y, 'b')
EDU>> axis tight
EDU>> set(gca, 'color', 'none')
EDU>> legend('X', 'Y')
EDU>> xlabel('time (s)')
EDU>> ylabel('position (deg)');
EDU>> suptitle([basename(pf.src) 'uncal, tr#1, fr#5'])
EDU>> 