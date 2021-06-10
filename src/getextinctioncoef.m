function [eHBO2,eHB,muaw,eicg]=getextinctioncoef(lambdas)
%Last Edited 03/18/05 by TD
%Loads necessary functions for OIS quantitifcation. Requires hemoglobin.dat, newwater.dat, lipid.dat
% Modified to get rid of lipid, since lipid doesn't have data for OIS wavelength, 01/16/05, by Chao
%load the extinction coeffs from a variety of sources.
%
%The units of the hbo2 and hb extinction coefficients in file hemoglobin.dat are 1/(cm*uM)
%The units of the absorption coefficient for pure water in newwater.dat are
%1/cm
%
%lipidconc and waterconc should be in percentage. NOT USED FOR OIS
%
%Dat is obtained from Scott Prahl's website.
%
%load the extinction coefficients needed Units are in 1/(cm*M)
%Load Differential Pathlength Factors, which are in units of cm
% From Steve Jacques' web site : Gratzer, Kollias
% Extinction Coefficients at 750 nm, 786 nm, 830 nm
%
%[eHBO2,eHB,muaw,eicg]=getextinctioncoef(lambdas)
load ../data/hemoglobin.dat;

indH = zeros(size(lambdas));

for tt=1:length(lambdas)
   indH(tt) = find(hemoglobin(:,1) == lambdas(tt));
end

eHBO2 = hemoglobin(indH,2)*log(10)*10^(-6); %The log(10) multiplication converts from base 10 to base e, See Huber, Phys Med Biol 46, 2001, the 10^(-6) is to go from M to uM
eHB   = hemoglobin(indH,3)*log(10)*10^(-6);

if nargout > 2
    % Mua from water (Segelstein) : interpolated data
    load ../data/newwater.dat;
    indW = zeros(size(lambdas));
    for tt=1:length(lambdas)
      indW(tt) = find(newwater(:,1) == lambdas(tt));
    end
    muaw = newwater(indW,2);

    %ICG Concentration
    load ../data/icg.dat
    %this reads in a matrix icg, columns are wavelengths, 6.5 uM spectra,
    %65 uM spectra, 650 uM spectra, 1290 uM spectra
    
    indicg = zeros(size(lambdas));
    for tt = 1:length(lambdas) 
        if lambdas(tt) <= 900
            indicg(tt) = find(icg(:,1) == lambdas(tt));
        else
           indicg(tt) = nan;
        end
    end
    eicg = zeros(size(eHB));
    I = isnan(indicg);
    eicg(~I) = icg(indicg(~I),2)*log(10)*10^(-6);
    eicg(I) = 0;
end

