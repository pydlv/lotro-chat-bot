unit ProcessHandlerUnit;

{$MODE Delphi}

{
Will handle all process specific stuff like openening and closing a process
The ProcessHandler variable will be in cefuncproc, but a tabswitch to another
process will set it to the different tab's process
}

interface

uses LCLIntf, newkernelhandler, classes;

type
  TSystemArchitecture=(archX86=0, archArm=1);

type TProcessHandler=class
  private
    fis64bit: boolean;
    fprocesshandle: THandle;
    fpointersize: integer;
    fSystemArchitecture: TSystemArchitecture;
    procedure setIs64bit(state: boolean);
    procedure setProcessHandle(processhandle: THandle);
  public
    processid: dword;


    procedure Open;
    property is64Bit: boolean read fIs64Bit;
    property pointersize: integer read fPointersize;
    property processhandle: THandle read fProcessHandle write setProcessHandle;
    property SystemArchitecture: TSystemArchitecture read fSystemArchitecture;
end;

implementation

procedure TProcessHandler.setIs64bit(state: boolean);
begin
  fis64bit:=state;
  if state then
  begin
    fpointersize:=8;
  end
  else
  begin
    fpointersize:=4;
  end;
end;

procedure TProcessHandler.setProcessHandle(processhandle: THandle);
begin
  fprocesshandle:=processhandle;
  setIs64Bit(newkernelhandler.Is64BitProcess(fProcessHandle));

//  if (mainform<>nil) and (mainform.addresslist<>nil) then
//    mainform.addresslist.needsToReinterpret:=true;
end;

procedure TProcessHandler.Open;
begin

end;

end.

