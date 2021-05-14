function varargout = col_proj_map(varargin)
% COL_PROJ_MAP MATLAB code for col_proj_map.fig
%      COL_PROJ_MAP, by itself, creates a new COL_PROJ_MAP or raises the existing
%      singleton*.
%
%      H = COL_PROJ_MAP returns the handle to a new COL_PROJ_MAP or the handle to
%      the existing singleton*.
%
%      COL_PROJ_MAP('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in COL_PROJ_MAP.M with the given input arguments.
%
%      COL_PROJ_MAP('Property','Value',...) creates a new COL_PROJ_MAP or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before col_proj_map_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to col_proj_map_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help col_proj_map

% Last Modified by GUIDE v2.5 10-May-2019 12:28:30

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @col_proj_map_OpeningFcn, ...
                   'gui_OutputFcn',  @col_proj_map_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT

% --- Executes just before col_proj_map is made visible.
function col_proj_map_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to col_proj_map (see VARARGIN)

% Choose default command line output for col_proj_map
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% This sets up the initial plot - only do when we are invisible
% so window can get raised using col_proj_map.

% UIWAIT makes col_proj_map wait for user response (see UIRESUME)
% uiwait(handles.figure1);

addpath('.')

global processed;
processed = false;
global FileImported;
FileImported = false;
global axesUpdated;
axesUpdated = false;

global projXYPlane;
global projXZPlane;
global projYZPlane;

projXYPlane=1;
projXZPlane=0;
projYZPlane=0;

txt1 = 'Column Projection Analysis for RMC6F';
t1=text(0.06,0.96,txt1);
t1.FontSize = 23;
t1.FontWeight = 'bold';
txt2 = 'Author: Maksim Eremenko & Yuanpeng Zhang';
t2=text(0.125,0.85,txt2);
t2.FontSize = 18;
txt3 = 'National Institute of Standards and Technology';
t3=text(0.075,0.55,txt3);
t3.FontSize = 20;
txt4 = 'Oak Ridge National Laboratory';
t4=text(0.215,0.45,txt4);
t4.FontSize = 20;
txt5 = 'Email: zyroc1990@gmail.com';
t5=text(0.22,0.18,txt5);
t5.FontSize = 20;
drawnow

% --- Outputs from this function are returned to the command line.
function varargout = col_proj_map_OutputFcn(hObject, eventdata, handles)
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;

% --------------------------------------------------------------------
function FileMenu_Callback(hObject, eventdata, handles)
% hObject    handle to FileMenu (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% --------------------------------------------------------------------
function OpenMenuItem_Callback(hObject, eventdata, handles)
% hObject    handle to OpenMenuItem (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
file = uigetfile('*.fig');
if ~isequal(file, 0)
    open(file);
end

% --------------------------------------------------------------------
function PrintMenuItem_Callback(hObject, eventdata, handles)
% hObject    handle to PrintMenuItem (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
printdlg(handles.figure1)

% --------------------------------------------------------------------
function CloseMenuItem_Callback(hObject, eventdata, handles)
% hObject    handle to CloseMenuItem (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
selection = questdlg(['Close ' get(handles.figure1,'Name') '?'],...
                     ['Close ' get(handles.figure1,'Name') '...'],...
                     'Yes','No','Yes');
if strcmp(selection,'No')
    return;
end

delete(handles.figure1)

% --- Executes on button press in importButton.
function importButton_Callback(hObject, eventdata, handles)
% hObject    handle to importButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global NumberOfAtoms;
global SuperCell;
global Cell;
global AtomTypesL;
global RMC_Data;
global FileImported;
axes(handles.axes1);
cla;

[FileName,PathName]= uigetfile('*.rmc6f','Choose RMC6f File');

if isnumeric(FileName) && isnumeric(PathName)
    if FileName==0 && PathName==0
        return
    end
end

File=[PathName FileName];
Read_RMC6f(File);

FileImported = true;

set(handles.selectAtomType,'string',[{'Select Atom Type'};AtomTypesL])

global axesUpdated;
if ~axesUpdated
    cla
    txt1 = 'RMC6F file successfull read in!';
    txt2 = 'Select an atom type from list and project columns!';
    t1=text(0.3,0.55,txt1);
    t2=text(0.18,0.45,txt2);
    t1.FontSize = 15;
    t2.FontSize = 15;
    drawnow
else
    cla
    txt1 = 'RMC6F file successfull read in!';
    txt2 = 'Select an atom type from list and project columns!';
    t1=text(0.33,0.55,txt1);
    t2=text(0.24,0.45,txt2);
    t1.FontSize = 15;
    t2.FontSize = 15;
    drawnow
end

% --- Executes on button press in projectButton.
function projectButton_Callback(hObject, eventdata, handles)
% hObject    handle to projectButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global AtomSelected;
global AtomTypesL;
global FileImported;
global axesUpdated;

global projXYPlane;
global projXZPlane;
global projYZPlane;

if ~FileImported
    cla
    txt = 'Import a RMC6f configuration file first!';
    t=text(0.16,0.52,txt);
    t.FontSize = 20;
    drawnow
    return
end

if strcmp(AtomSelected, 'Select Atom Type')
    if axesUpdated
        cla
        txt = 'Select an atom type from the dropdown list first!';
        t=text(0.145,0.52,txt);
        t.FontSize = 20;
        drawnow
        return
    else
        cla
        txt = 'Select an atom type from the dropdown list first!';
        t=text(0.065,0.52,txt);
        t.FontSize = 20;
        drawnow
        return
    end
end

cla
txt = 'Processing...';
t=text(0.35,0.52,txt);
t.FontSize = 30;
drawnow

SelectedAtomIndex = find(ismember(AtomTypesL, AtomSelected));

referenceElementsNumbers=[SelectedAtomIndex]; %Atom type number in the rmc6f file;
referencePercent=3.1; %Maximum deviation from the average position;

global RMC_Data;
global SuperCell;
global Cell;

[MeanRMCData,MeanCoord,MeanPosCoord,DisplCoord] = PosMeanCoord(RMC_Data,SuperCell);

Elements=unique(table2array(MeanRMCData(:,2)),'stable');

A = cell(length(referenceElementsNumbers),1);
for i=1:length(referenceElementsNumbers)
    A{i}=find(strcmp(table2array(RMC_Data(:,2)),...
      table2array(Elements(referenceElementsNumbers(i)))));
end
referenceNumbrList=vertcat(A{:});
referenceMeanCoord=MeanCoord(vertcat(A{:}),1:3); % A

if ~isnumeric(table2array(RMC_Data(1,3)))
    Coord=table2array(RMC_Data(:,4:6));
else
    Coord=table2array(RMC_Data(:,3:5));
end

referenceCoordTmp=Coord(vertcat(A{:}),1:3);

referenceCoordTmp(abs(referenceCoordTmp-referenceMeanCoord)>0.5)=...
  referenceCoordTmp(abs(referenceCoordTmp-referenceMeanCoord)>0.5)-1;

referenceElementslist=MeanRMCData(vertcat(A{:}),2);  

referenceUniqueX=unique(referenceMeanCoord(:,1));
referenceUniqueY=unique(referenceMeanCoord(:,2));
referenceUniqueZ=unique(referenceMeanCoord(:,3));

referencePercent=referencePercent/100;
referenceDelta=(referencePercent*1)./SuperCell;

for i=1:length(referenceUniqueX)
    tmp=find(and(referenceUniqueX<(referenceUniqueX(i)+referenceDelta(1)),...
      referenceUniqueX>(referenceUniqueX(i)-referenceDelta(1))));
    referenceUniqueX(tmp)=mean(referenceUniqueX(tmp));
    clear tmp;
end
for i=1:length(referenceUniqueY)
    tmp=find(and(referenceUniqueY<(referenceUniqueY(i)+referenceDelta(2)),...
      referenceUniqueY>(referenceUniqueY(i)-referenceDelta(2))));
    referenceUniqueY(tmp)=mean(referenceUniqueY(tmp));
    clear tmp;
end
for i=1:length(referenceUniqueZ)
    tmp=find(and(referenceUniqueZ<(referenceUniqueZ(i)+referenceDelta(3)),...
      referenceUniqueZ>(referenceUniqueZ(i)-referenceDelta(3))));
    referenceUniqueZ(tmp)=mean(referenceUniqueZ(tmp));
    clear tmp;
end

referenceUniqueX=unique(referenceUniqueX);
referenceUniqueY=unique(referenceUniqueY);
referenceUniqueZ=unique(referenceUniqueZ);

for i=1:length(referenceUniqueX)
    referenceMeanCoord(and(referenceMeanCoord(:,1)<(referenceUniqueX(i)+...
      referenceDelta(1)),referenceMeanCoord(:,1)>(referenceUniqueX(i)-...
      referenceDelta(1))),1)=referenceUniqueX(i);
end
for i=1:length(referenceUniqueY)
    referenceMeanCoord(and(referenceMeanCoord(:,2)<(referenceUniqueY(i)+...
      referenceDelta(2)),referenceMeanCoord(:,2)>(referenceUniqueY(i)-...
      referenceDelta(2))),2)=referenceUniqueY(i);
end
for i=1:length(referenceUniqueZ)
    referenceMeanCoord(and(referenceMeanCoord(:,3)<(referenceUniqueZ(i)+...
      referenceDelta(3)),referenceMeanCoord(:,3)>(referenceUniqueZ(i)-...
      referenceDelta(3))),3)=referenceUniqueZ(i);
end

global ST;
if (projXZPlane==1)
    s=0;
    for i=1:length(referenceUniqueX)
      for j=1:length(referenceUniqueZ)  
        for k=1:1    
            RNumbers=find((referenceMeanCoord(:,1)==referenceUniqueX(i))&...
             (referenceMeanCoord(:,3)==referenceUniqueZ(j))...
             &referenceNumbrList) ;
            lgth = length(RNumbers);  
            if((lgth>0))  
                s=s+1;   
                referenceColumnXZ(s).Count=lgth;
                %referenceColumnXZ(s).ElementNumber=referenceNumbrList;
                referenceColumnXZ(s).X=referenceUniqueX(i);
                referenceColumnXZ(s).Z=referenceUniqueZ(j);
                referenceColumnXZ(s).MeanX=mean(referenceCoordTmp(RNumbers,1));
                referenceColumnXZ(s).MeanZ=mean(referenceCoordTmp(RNumbers,3));
            end
        end
      end
    end

    ST=struct2table(referenceColumnXZ);

    distmax=5;
    for i=1:length(referenceColumnXZ)
        total=0;
        l=0;
        LettParam=0;
            for j=1:length(referenceColumnXZ) 
                if(i~=j)
                    deltaX=(referenceColumnXZ(i).MeanX-referenceColumnXZ(j).MeanX);
                    deltaZ=(referenceColumnXZ(i).MeanZ-referenceColumnXZ(j).MeanZ);
                    deltaXX=Cell(1,1)*(deltaX-fix(2*deltaX));
                    deltaZZ=Cell(3,1)*(deltaZ-fix(2*deltaZ));
                    dist=sqrt((deltaXX)*(deltaXX)+(deltaZZ)*(deltaZZ));
                    if (dist<distmax)
                        l=l+1;
                        LettParam(l)=dist;
                    end
                end 
            end
            if (l>0)
                referenceColumnXZ(i).LatticeConstant=mean(LettParam);
                clear LettParam;
            end 
         referenceColumnXZ(i).VLength=sqrt((referenceColumnXZ(i).X-...
           referenceColumnXZ(i).MeanX)^2+(referenceColumnXZ(i).Z-...
           referenceColumnXZ(i).MeanZ)^2);
    end

    ST=struct2table(referenceColumnXZ);
    az=length(referenceUniqueZ);
    ax=length(referenceUniqueX);

    colormap parula;
    Ic = round( ST.VLength/max(max(ST.VLength))*64);
    Ic( Ic == 0) = 1;

    quiver(ST.X,ST.Z,ST.X-ST.MeanX,ST.Z-ST.MeanZ);
    axis([0 1 0 1])
    set(gca,'YTickLabel',[]);
    set(gca,'XTickLabel',[]);
    set(gca,'xtick',[]);
    set(gca,'ytick',[]);
end

if (projXYPlane==1)
    s=0;
    for i=1:length(referenceUniqueX)
      for j=1:length(referenceUniqueY)  
        for k=1:1    
            RNumbers=find((referenceMeanCoord(:,1)==referenceUniqueX(i))&...
             (referenceMeanCoord(:,2)==referenceUniqueY(j))...
             &referenceNumbrList) ;
            lgth = length(RNumbers);  
            if((lgth>0))  
                s=s+1;   
                referenceColumnXY(s).Count=lgth;
                referenceColumnXY(s).X=referenceUniqueX(i);
                referenceColumnXY(s).Y=referenceUniqueY(j);
                referenceColumnXY(s).MeanX=mean(referenceCoordTmp(RNumbers,1));
                referenceColumnXY(s).MeanY=mean(referenceCoordTmp(RNumbers,2));
            end
        end
      end
    end

    ST=struct2table(referenceColumnXY);

    distmax=5;
    for i=1:length(referenceColumnXY)
        total=0;
        l=0;
        LettParam=0;
            for j=1:length(referenceColumnXY) 
                if(i~=j)
                    deltaX=(referenceColumnXY(i).MeanX-referenceColumnXY(j).MeanX);
                    deltaY=(referenceColumnXY(i).MeanY-referenceColumnXY(j).MeanY);
                    deltaXX=Cell(1,1)*(deltaX-fix(2*deltaX));
                    deltaYY=Cell(3,1)*(deltaY-fix(2*deltaY));
                    dist=sqrt((deltaXX)*(deltaXX)+(deltaYY)*(deltaYY));
                    if (dist<distmax)
                        l=l+1;
                        LettParam(l)=dist;
                    end
                end 
            end
            if (l>0)
                referenceColumnXY(i).LatticeConstant=mean(LettParam);
                clear LettParam;
            end 
         referenceColumnXY(i).VLength=sqrt((referenceColumnXY(i).X-...
           referenceColumnXY(i).MeanX)^2+(referenceColumnXY(i).Y-...
           referenceColumnXY(i).MeanY)^2);
    end

    ST=struct2table(referenceColumnXY);
    ay=length(referenceUniqueY);
    ax=length(referenceUniqueX);

    colormap parula;
    Ic = round( ST.VLength/max(max(ST.VLength))*64);
    Ic( Ic == 0) = 1;

    quiver(ST.X,ST.Y,ST.X-ST.MeanX,ST.Y-ST.MeanY);
    axis([0 1 0 1])
    set(gca,'YTickLabel',[]);
    set(gca,'XTickLabel',[]);
    set(gca,'xtick',[]);
    set(gca,'ytick',[]);
end

if (projYZPlane==1)
    s=0;
    for i=1:length(referenceUniqueY)
      for j=1:length(referenceUniqueZ)  
        for k=1:1
            RNumbers=find((referenceMeanCoord(:,2)==referenceUniqueY(i))&...
             (referenceMeanCoord(:,3)==referenceUniqueZ(j))...
             &referenceNumbrList) ;
            lgth = length(RNumbers);  
            if((lgth>0))  
                s=s+1;   
                referenceColumnYZ(s).Count=lgth;
                %referenceColumnXZ(s).ElementNumber=referenceNumbrList;
                referenceColumnYZ(s).Y=referenceUniqueY(i);
                referenceColumnYZ(s).Z=referenceUniqueZ(j);
                referenceColumnYZ(s).MeanY=mean(referenceCoordTmp(RNumbers,2));
                referenceColumnYZ(s).MeanZ=mean(referenceCoordTmp(RNumbers,3));
            end
        end
      end
    end

    ST=struct2table(referenceColumnYZ);

    distmax=5;
    for i=1:length(referenceColumnYZ)
        total=0;
        l=0;
        LettParam=0;
            for j=1:length(referenceColumnYZ) 
                if(i~=j)
                    deltaY=(referenceColumnYZ(i).MeanY-referenceColumnYZ(j).MeanY);
                    deltaZ=(referenceColumnYZ(i).MeanZ-referenceColumnYZ(j).MeanZ);
                    deltaYY=Cell(1,1)*(deltaY-fix(2*deltaY));
                    deltaZZ=Cell(3,1)*(deltaZ-fix(2*deltaZ));
                    dist=sqrt((deltaYY)*(deltaYY)+(deltaZZ)*(deltaZZ));
                    if (dist<distmax)
                        l=l+1;
                        LettParam(l)=dist;
                    end
                end 
            end
            if (l>0)
                referenceColumnYZ(i).LatticeConstant=mean(LettParam);
                clear LettParam;
            end 
         referenceColumnYZ(i).VLength=sqrt((referenceColumnYZ(i).Y-...
           referenceColumnYZ(i).MeanY)^2+(referenceColumnYZ(i).Z-...
           referenceColumnYZ(i).MeanZ)^2);
    end

    ST=struct2table(referenceColumnYZ);
    az=length(referenceUniqueZ);
    ay=length(referenceUniqueY);

    colormap parula;
    Ic = round( ST.VLength/max(max(ST.VLength))*64);
    Ic( Ic == 0) = 1;

    quiver(ST.Y,ST.Z,ST.Y-ST.MeanY,ST.Z-ST.MeanZ);
    axis([0 1 0 1])
    set(gca,'YTickLabel',[]);
    set(gca,'XTickLabel',[]);
    set(gca,'xtick',[]);
    set(gca,'ytick',[]);
end

global processed;
processed = true;
axesUpdated = true;

% --- Executes on button press in outputButton.
function outputButton_Callback(hObject, eventdata, handles)
% hObject    handle to outputButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global ST;
global processed;
global AtomSelected;
global axesUpdated;

if strcmp(AtomSelected, 'Select Atom Type') || ~processed
    if ~axesUpdated
        cla
        txt = 'Execute the column projection first!';
        t=text(0.175,0.52,txt);
        t.FontSize = 20;
        drawnow
        return
    else
        cla
        txt = 'Execute the column projection first!';
        t=text(0.235,0.52,txt);
        t.FontSize = 20;
        drawnow
        return
    end
end

filter = {'*.txt';'*.dat';'*.out';'*.*'};
[OutFileName,OutPathName]= uiputfile(filter,'Output Column Projection',...
  strcat('col_proj_',AtomSelected,'.txt'));
if isnumeric(OutFileName) && isnumeric(OutPathName)
    if OutFileName==0 && OutPathName==0
        return
    end
end
OutFile=[OutPathName OutFileName];
writetable(ST,OutFile,'Delimiter',' ')

% --- Executes on button press in clearButton.
function clearButton_Callback(hObject, eventdata, handles)
% hObject    handle to clearButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
cla
global processed;
processed = false;
global axesUpdated;
if ~axesUpdated
    txt1 = 'Column Projection Analysis for RMC6F';
    t1=text(0.06,0.96,txt1);
    t1.FontSize = 23;
    t1.FontWeight = 'bold';
    txt2 = 'Author: Maksim Eremenko & Yuanpeng Zhang';
    t2=text(0.125,0.85,txt2);
    t2.FontSize = 18;
    txt3 = 'National Institute of Standards and Technology';
    t3=text(0.075,0.55,txt3);
    t3.FontSize = 20;
    txt4 = 'Oak Ridge National Laboratory';
    t4=text(0.215,0.45,txt4);
    t4.FontSize = 20;
    txt5 = 'Email: zyroc1990@gmail.com';
    t5=text(0.22,0.18,txt5);
    t5.FontSize = 20;
    drawnow
else
    txt1 = 'Column Projection Analysis for RMC6F';
    t1=text(0.14,0.96,txt1);
    t1.FontSize = 23;
    t1.FontWeight = 'bold';
    txt2 = 'Author: Maksim Eremenko & Yuanpeng Zhang';
    t2=text(0.192,0.85,txt2);
    t2.FontSize = 18;
    txt3 = 'National Institute of Standards and Technology';
    t3=text(0.153,0.55,txt3);
    t3.FontSize = 20;
    txt4 = 'Oak Ridge National Laboratory';
    t4=text(0.27,0.45,txt4);
    t4.FontSize = 20;
    txt5 = 'Email: zyroc1990@gmail.com';
    t5=text(0.275,0.18,txt5);
    t5.FontSize = 20;
    drawnow
end

% --- Executes on selection change in selectAtomType.
function selectAtomType_Callback(hObject, eventdata, handles)
% hObject    handle to selectAtomType (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = get(hObject,'String') returns selectAtomType contents as cell array
%        contents{get(hObject,'Value')} returns selected item from selectAtomType
contents = get(hObject,'String');
global AtomSelected;
AtomSelected = contents{get(hObject,'Value')};
global processed;
processed = false;

% --- Executes during object creation, after setting all properties.
function selectAtomType_CreateFcn(hObject, eventdata, handles)
% hObject    handle to selectAtomType (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
     set(hObject,'BackgroundColor','white');
end

set(hObject, 'String', {'Select Atom Type'});

contents = get(hObject,'String');
global AtomSelected;
AtomSelected = contents{get(hObject,'Value')};

% --- Executes during object creation, after setting all properties.
function axes1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to axes1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: place code in OpeningFcn to populate axes1
set(gca,'YTickLabel',[]);
set(gca,'XTickLabel',[]);
set(gca,'xtick',[]);
set(gca,'ytick',[]);

% --------------------------------------------------------------------
function saveFigButton_ClickedCallback(hObject, eventdata, handles)
% hObject    handle to saveFigButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global processed;
global axesUpdated;
if ~processed
    if axesUpdated
        cla
        txt = 'Execute the column projection first!';
        t=text(0.235,0.52,txt);
        t.FontSize = 20;
        drawnow
        return
    else
        cla
        txt = 'Execute the column projection first!';
        t=text(0.175,0.52,txt);
        t.FontSize = 20;
        drawnow
        return
    end
end
filter = {'*.png';'*.eps';'*.bmp'};
[OutFileName,OutPathName]= uiputfile(filter,'Save Figure',...
  '*.png');
if isnumeric(OutFileName) && isnumeric(OutPathName)
    if OutFileName==0 && OutPathName==0
        return
    end
end
OutFile=[OutPathName OutFileName];
F = getframe(handles.axes1);
Image = frame2im(F);
imwrite(Image, OutFile);

% --------------------------------------------------------------------
% Function for reading in the rmc6f configuration.
function Read_RMC6f(File)
fid = fopen(File,'r');

global axesUpdated;
if ~axesUpdated
    cla
    txt = 'Reading in the RMC6F file...';
    t=text(0.32,0.52,txt);
    t.FontSize = 15;
    drawnow
else
    cla
    txt = 'Reading in the RMC6F file...';
    t=text(0.35,0.52,txt);
    t.FontSize = 15;
    drawnow
end

RMC6fHeaderCell = textscan(fid,'%s',50,'Delimiter','\n');
RMC6fHeader=cell2table(RMC6fHeaderCell{1,1});
refString='Atoms';
AtomsStrIndex = strfind(RMC6fHeader{:,1},refString);
AtomsStrIndex = find(~cellfun(@isempty,AtomsStrIndex));
refString='Supercell dimensions:';
SupercellStrIndex = strfind(RMC6fHeader{:,1},refString);
SupercellStrIndex = ~cellfun(@isempty,SupercellStrIndex);

str = char(RMC6fHeader{SupercellStrIndex,1});
if isempty(str)
    cla
    txt = 'Necessary supercell dimensions not found in the provided RMC6F file!';
    t=text(0.025,0.52,txt);
    t.FontSize = 15;
    drawnow
    return
end
Key   = ':';
Index = strfind(str, Key);
global SuperCell;
SuperCell = sscanf(str(Index(1) + length(Key):end), '%u', 3);

refString='Number of atoms:';
NumberOfAtomsStrIndex = strfind(RMC6fHeader{:,1},refString);
NumberOfAtomsStrIndex = ~cellfun(@isempty,NumberOfAtomsStrIndex);
str = char(RMC6fHeader{NumberOfAtomsStrIndex,1});
Key   = ':';
Index = strfind(str, Key);
global NumberOfAtoms;
NumberOfAtoms = sscanf(str(Index(1) + length(Key):end), '%u', 1);

refString='Cell (Ang/deg):';
CellStrIndex = strfind(RMC6fHeader{:,1},refString);
CellStrIndex = ~cellfun(@isempty,CellStrIndex);
str = char(RMC6fHeader{CellStrIndex,1});
Key   = ':';
Index = strfind(str, Key);
global Cell;
Cell = sscanf(str(Index(1) + length(Key):end), '%g', 6);

global RMC_Data;
RMC_Data = readtable(File,'Filetype', 'text','HeaderLines',...
    AtomsStrIndex, 'ReadRowNames',false,'ReadVariableNames',false);

global AtomTypesL;
AtomTypesLT = table2array(RMC_Data(:,2));
AtomTypesL = unique(AtomTypesLT,'stable');

% --------------------------------------------------------------------
% Function for calculating mean positions.
function [MeanRMCData,MeanCoordXYZ,MeanPosCoord,DisplCoord] = ...
           PosMeanCoord(RMC_Data,SuperCell)
% Determine type of RMC6F file.
if ~isnumeric(table2array(RMC_Data(1,3)))
    CoordXYZ=table2array(RMC_Data(:,4:6));
    Pos = table2array(RMC_Data(:,7));
    CellXYZ=table2array(RMC_Data(:,8:10));
else
    CoordXYZ=table2array(RMC_Data(:,3:5));
    Pos = table2array(RMC_Data(:,6));
    CellXYZ=table2array(RMC_Data(:,7:9));
end

UniquePositions = unique(Pos);
DisplCoord=zeros(length(CoordXYZ(:,1)),3);
%displacement from Cell start position
for j = 1:3
    DisplCoord(:,j)=CoordXYZ(:,j)-CellXYZ(:,j)/SuperCell(j);
    DisplCoord(:,j)=DisplCoord(:,j)-fix(2*DisplCoord(:,j));
end 

MeanCoordXYZ=DisplCoord;

MeanPosCoord=zeros(length(UniquePositions),3);
%mean displacement for reference number
for i = 1:length(UniquePositions)
    for j = 1:3
        MeanPosCoord(i,j) = mean(DisplCoord(Pos==UniquePositions(i),j));
        MeanCoordXYZ(Pos==UniquePositions(i),j)=MeanPosCoord(i,j)+...
          CellXYZ(Pos==UniquePositions(i),j)/SuperCell(j);
    end
end
MeanRMCData=RMC_Data;
if ~isnumeric(table2array(RMC_Data(1,3)))
    MeanRMCData(:,4:6)=array2table(MeanCoordXYZ);
else
    MeanRMCData(:,3:5)=array2table(MeanCoordXYZ);
end


% --- Executes on button press in xyPlane.
function xyPlane_Callback(hObject, eventdata, handles)
% hObject    handle to xyPlane (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of xyPlane
global projXYPlane;
global projXZPlane;
global projYZPlane;
projXYPlane=get(hObject,'Value');
projXZPlane=0;
projYZPlane=0;

% --- Executes on button press in xzPlane.
function xzPlane_Callback(hObject, eventdata, handles)
% hObject    handle to xzPlane (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of xzPlane
global projXYPlane;
global projXZPlane;
global projYZPlane;
projXZPlane=get(hObject,'Value');
projXYPlane=0;
projYZPlane=0;

% --- Executes on button press in yzPlane.
function yzPlane_Callback(hObject, eventdata, handles)
% hObject    handle to yzPlane (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of yzPlane
global projXYPlane;
global projXZPlane;
global projYZPlane;
projYZPlane=get(hObject,'Value');
projXYPlane=0;
projXZPlane=0;
