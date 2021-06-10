filename = '/Users/thomasusherwood/lab_code/elliott_lab/PDD_project/IR-RED-AIF/data/ICG02_PIG006_Volts_20201111_125109.xls';
fid = fopen(filename);
X1 = textscan(fid,'%f %f %f %f %f %f','Headerlines',6);
fclose(fid);

fs = 500; %sampling rate
tbl = [10 60]; %reliable baseline data.

% red and ir channels (raw)
RED = X1{5}; 
IR = X1{6};

% baseline signal from which to calculate heart-rate
RED_base = RED(1000:41000);
size(RED_base)
IR_base = IR(1000:41000);
size(IR_base)

% powerspectrum
[P,f] = pwelch([RED_base IR_base],[],[],[],fs);
size(P)
size(f)
fprintf('f start: %f\nf end: %f\n',f(1),f(end))

bpm = f*60; 

% get heart-rate
figure;
plot(bpm,P);title('select the center of the heart-rate peak'); 
xlim([12 180]); 
xlabel('frequency (beats per min).');
[ghr,~]=ginput(1);
fhr = ghr/60;
close(gcf);