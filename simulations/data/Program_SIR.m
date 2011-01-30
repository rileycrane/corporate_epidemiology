function [t,X,Y] = Program_SIR(N, Size, beta, gamma, alpha , Y0, timestep, MaxTime)

% Sets up default parameters if necessary.
if nargin == 0
    N=1000;
    Size=10;
    beta=1;
    gamma=0.5;
    Y0=4;
    timestep=0.1;
    MaxTime=100;
end

data1=importdata('ir_interactions.txt');

X=[data1(:,1)' data1(:,2)']; %create array of individuals
[S IX]=sort(X); %sort
[h x]=hist(S,0:1:300); 
NUMS=x(find(h>0)); %get used numbers only


for i=1:1:length(NUMS)
    XNUM(NUMS(i)+1) = i;
end

data2=XNUM(1+data1(:,1))';
data2(:,2)=XNUM(1+data1(:,2));

data2(:,3)=floor(data1(:,3)/374400);%secs since start
data2(:,4)=floor((data1(:,4)-data1(:,3))/374400);

N=max(XNUM);
[s2 ix2] = sort(data2(:,3));
D=data2(ix2,1:4);

% Checks all the parameters are valid
CheckGreater(N,0,'Individuals N ');
CheckGreater(beta,0,'beta');
CheckGreaterOrEqual(gamma,0,'gamma');
CheckGreater(Y0,0,'number of infections Y0');

% Set Up a 10x10 grid and position individuals
x=Size*rand(N,1); y=Size*rand(N,1); 
Status=zeros(N,1); %all susceptible
for i=1:1:Y0
    Status(floor((N-1)*rand(1))+1)=1;
end


t=0; i=1; X=length(find(Status==0)); Y=length(find(Status==1)); i=i+1;
% The main iteration
for ti=1:1:length(D)
    
     if(Status(D(ti,1))==0 & Status(D(ti,2))==1)
        timestep = D(ti,4); 
        Q=1-exp(-timestep*beta);
        if(Q>=rand(1))
            Status(D(ti,1))=1;
        end
     elseif(Status(D(ti,1))==1 & Status(D(ti,2))==0)
        timestep = D(ti,4); 
        Q=1-exp(-timestep*beta);
        if(Q>=rand(1))
            Status(D(ti,2))=1;
        end
     end

    Sus=find(Status==0); Inf=find(Status==1); Emp=find(Status==2);
    X(ti)=length(Sus); Y(ti)=length(Inf);
    t(ti)=D(ti,3);


    % plots the data
    subplot(2,1,1);
    plot([x(D(ti,1)) x(D(ti,2))],[y(D(ti,1)) y(D(ti,2))],'-k')
    hold on
    plot(x(Emp),y(Emp),'.k','MarkerSize',8,'Color',[0.5 0.5 0.5]);
    hold on
    plot(x(Sus),y(Sus),'ok','MarkerFaceColor','g');
    plot(x(Inf),y(Inf),'sk','MarkerFaceColor','r');
    
    hold off
    axis([0 Size 0 Size]);

    subplot(4,1,3);
    plot(t,X,'-g');
    ylabel 'Total Susceptibles'

    subplot(4,1,4);
    plot(t,Y,'-r');
    ylabel 'Total Infecteds'
    xlabel 'Time'
    drawnow
    
end



% Does a simple check on the value
function []=CheckGreaterOrEqual(Parameter, Value, str)
m=find(Parameter<Value);
if length(m)>0
    error('Parameter %s(%g) (=%g) is less than %g',str,m(1),Parameter(m(1)),Value);
end

function []=CheckGreater(Parameter, Value, str)
m=find(Parameter<=Value);
if length(m)>0
    error('Parameter %s(%g) (=%g) is less than or equal to %g',str,m(1),Parameter(m(1)),Value);
end

function []=CheckLess(Parameter, Value, str)
m=find(Parameter>=Value);
if length(m)>0
    error('Parameter %s(%g) (=%g) is greater than or equal to %g',str,m(1),Parameter(m(1)),Value);
end

