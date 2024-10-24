import maya.cmds as cmds
from PySide2 import QtWidgets,QtGui,QtCore
from maya.app.general import mayaMixin
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import shutil


#  エラー用ダイアログ
class ErrorWindow(mayaMixin.MayaQWidgetBaseMixin,QtWidgets.QWidget):
    def __init__(self,eText):
        super().__init__()
        self.msgBox = QtWidgets.QMessageBox()
        self.msgBox.setWindowTitle(self.tr("Error"))
        self.msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        
        messages = [self.tr('Please choose save folder'),self.tr('Path must in the subpath'),self.tr('Path must in the subpath'),self.tr('This material is the default.\nCreation has stopped'),self.tr('Please choose copy folder'),self.tr('File has already exists.\nDo you want to replace it?'),self.tr('Please select a Material.'),self.tr('Please select a StandardSurface Material.')]

        self.msgBox.setText(messages[eText-1])
        self.ok = self.msgBox.addButton(QtWidgets.QMessageBox.Ok)
        self.msgBox.exec()
        closeOldWindow("Error")

class MainWindow(mayaMixin.MayaQWidgetBaseMixin,QtWidgets.QWidget):
    def __init__(self,title,translator):
        super().__init__()
        
        self.translator = translator
        self.setWindowTitle(title)
        layout = QtWidgets.QVBoxLayout()
        
        #  言語選択
        layout1 = QtWidgets.QHBoxLayout()
        self.combobox1 = QtWidgets.QComboBox(self)
        self.combobox1.addItems(["日本語", "English"])
        self.combobox1.currentIndexChanged.connect(self.langSwitch)
        layout1.addWidget(self.combobox1)
        layout.addLayout(layout1)
        
        self.label1 = QtWidgets.QLabel(self.tr("<b>Save folder</b>"))
        self.label1.setMargin(5)
        layout.addWidget(self.label1)

        self.checkbox1 = QtWidgets.QCheckBox(self.tr("Relative path"))
        layout.addWidget(self.checkbox1)

        layout2 = QtWidgets.QHBoxLayout()
        self.textbox1 = QtWidgets.QLineEdit(self.tr("Save Path"))
        layout2.addWidget(self.textbox1)
        self.button1 = QtWidgets.QPushButton("...")
        self.button1.clicked.connect(self.pushed_button1)
        layout2.addWidget(self.button1)
        layout.addLayout(layout2)

        self.label2 = QtWidgets.QLabel(self.tr("<b>Filename</b>"))
        self.label2.setMargin(5)
        layout.addWidget(self.label2)

        layout3 = QtWidgets.QHBoxLayout()
        self.textbox2 = QtWidgets.QLineEdit("standardSurface")
        layout3.addWidget(self.textbox2)
        self.button2 = QtWidgets.QPushButton(self.tr("Use material name"))
        self.button2.clicked.connect(self.pushed_button2)
        layout3.addWidget(self.button2)
        layout.addLayout(layout3)

        self.label3 = QtWidgets.QLabel(self.tr("<b>Copy Texture</b>"))
        self.label3.setMargin(5)
        layout.addWidget(self.label3)
        self.checkbox2 = QtWidgets.QCheckBox(self.tr("Copy"))
        layout.addWidget(self.checkbox2)
        
        layout4 = QtWidgets.QHBoxLayout()
        self.textbox3 = QtWidgets.QLineEdit(self.tr("Copy Path"))
        layout4.addWidget(self.textbox3)
        self.button3 = QtWidgets.QPushButton("...")
        self.button3.clicked.connect(self.pushed_button3)
        layout4.addWidget(self.button3)
        layout.addLayout(layout4)
        
        self.spacerItem1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(self.spacerItem1)
        
        self.frame = QtWidgets.QFrame()
        self.frame.setFrameShape(QtWidgets.QFrame.HLine)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(self.frame)
        
        self.button4 = QtWidgets.QPushButton(self.tr("Create"))
        self.button4.clicked.connect(self.pushed_button4)
        layout.addWidget(self.button4)

        self.setLayout(layout)
        self.setStyleSheet("QLabel { background-color : rgb(100,100,100); }")
    
    def pushed_button1(self):
        chpath = QtWidgets.QFileDialog.getExistingDirectory()
        if not chpath:
            return()
        path2= re.sub('.*sourceimages','sourceimages',chpath)
        self.textbox1.setText(path2)

    def pushed_button2(self):
        getname(self)

    def pushed_button3(self):
        chpath = QtWidgets.QFileDialog.getExistingDirectory()
        if not chpath:
            return()
        path2= re.sub('.*sourceimages','sourceimages',chpath)
        self.textbox3.setText(path2)

    def pushed_button4(self):
        mFolder = self.textbox1.text()
        check = Path(mFolder)
        if not check.is_dir():
            ErrorWindow(1)
            return()
        tFolder = self.textbox3.text()
        filename = self.textbox2.text()
        ch1 = self.checkbox1.isChecked()
        ch2 = self.checkbox2.isChecked()
        input = [mFolder,tFolder,filename,ch1,ch2]
        newAttr(input)
        
    def langSwitch(self):
        if self.combobox1.currentIndex() == 0:
            qm_file = r"mtlx_Jp.qm"
        else:
            qm_file = r"mtlx_En.qm"
    
        self.translator.load(qm_file,directory = cmds.workspace(q=True,rootDirectory=True)+'\\scripts\\i18n')
        QtCore.QCoreApplication.installTranslator(self.translator)
                
        self.label1.setText(self.tr("<b>Save folder</b>"))
        self.checkbox1.setText(self.tr("Relative path"))
        self.textbox1.setText(self.tr("Save Path"))
        self.label2.setText(self.tr("<b>Filename</b>"))
        self.textbox2.setText("standardSurface")
        self.button2.setText(self.tr("Use material name"))
        self.label3.setText(self.tr("<b>Copy Texture</b>"))
        self.checkbox2.setText(self.tr("Copy"))
        self.textbox3.setText(self.tr("Copy Path"))
        self.button4.setText(self.tr("Create"))
        
def convertRelative(target,current,copy):
    absp = Path(current).resolve()
    try:
        relp = absp.relative_to(target)
    except ValueError:
        ErrorWindow(2)
        return(None)
    return(str(relp).replace('\\','/'))

def newAttr(input):
    s = cmds.ls(sl=True)
    if checkname(s) == False:
        return()
    mxattr = ["base","base_color","diffuse_roughness","specular","specular_color","specular_roughness","specular_IOR","specular_anisotropy","specular_rotation","metalness","transmission","transmission_color","transmission_depth","transmission_scatter","transmission_scatter_anisotropy","transmission_dispersion","transmission_extra_roughness","subsurface","subsurface_color","subsurface_radius","subsurface_scale","subsurface_anisotropy","sheen","sheen_color","sheen_roughness","thin_walled","coat","coat_color","coat_roughness","coat_anisotropy","coat_rotation","coat_IOR","coat_affect_color","coat_affect_roughness","thin_film_thickness","thin_film_IOR","emission","emission_color","opacity","normal","displacement"]
    ssattr = ["base","baseColor","diffuseRoughness","specular","specularColor","specularRoughness","specularIOR","specularAnisotropy","specularRotation","metalness","transmission","transmissionColor","transmissionDepth","transmissionScatter","transmissionScatterAnisotropy","transmissionDispersion","transmissionExtraRoughness","subsurface","subsurfaceColor","subsurfaceRadius","subsurfaceScale","subsurfaceAnisotropy","sheen","sheenColor","sheenRoughness","thinWalled","coat","coatColor","coatRoughness","coatAnisotropy","coatRotation","coatIOR","coatAffectColor","coatAffectRoughness","thinFilmThickness","thinFilmIOR","emission","emissionColor","opacity"]
    newattr = []
    mxnodes = []
    ssnodes = []
    for i,attr in enumerate(ssattr):
        name = s[0] + '.' + attr
        value = cmds.getAttr(name)
        default = cmds.attributeQuery(attr, n=s[0], ld=True)
        if len(default) > 1:
            default = [tuple(default)]
        else:
            default = default[0]
        if value!=default:
            if isinstance(value,type(float)):
                types = 'float'
            elif isinstance(value,type(list)):
                types = 'color3'
                value = str(value[0][0])+', '+str(value[0][1])+', '+str(value[0][2])
            else:
                types = 'boolean'
                value = str.lower(str(value))
            newattr.append([mxattr[i],types,value])
            mxnodes.append(mxattr[i])
            ssnodes.append(attr)
    if newattr==[]:
        ErrorWindow(3)
        return()
    
    
    getNodePath(ssnodes,mxnodes,newattr,s,input)

def copytex(bfile,afolder):
    shutil.copy(bfile,afolder)

def getNodePath(ssnodes,mxnodes,newattr,s,input):
    paths=[]
    isfile=[]
    scl=0
    ssnodes.append('normalCamera')
    ssnodes.append('displacementShader')
    for i in ssnodes:
        attr = s[0]+'.'+i
        if i == 'normalCamera':
            nm = cmds.connectionInfo(attr,sfd=True)
            if(nm==''):
                continue
            nm = re.sub(r'\.(.*)', '',nm)
            attr = cmds.ls(nm)[0]+'.input'
            mxnodes.append('normal')
        if i == 'displacementShader':
            dis = cmds.listConnections(s[0],s=False,type='shadingEngine')
            attr = cmds.connectionInfo(dis[0]+'.displacementShader',sfd=True)
            if(attr==''):
                continue
            scl = cmds.ls(cmds.listConnections(dis[0],d=False,type='displacementShader'))[0].scale.get()
            mxnodes.append('height')
        if(con := cmds.connectionInfo(attr,sfd=True))!='':
            path = re.sub(r'\.(.*)', '',con)
            path = cmds.getAttr(cmds.ls(path)[0]+'.fileTextureName')
            paths.append(path)
            isfile.append(1)
        else:
            isfile.append(0)
    
    mFolder = str(input[0].replace('/','\\'))
    tFolder = input[1]
    filename = input[2]

    if input[4]:
        path=Path(tFolder)
        if not path.is_dir():
            ErrorWindow(4)
            return()
        if not path.exists():
            path.mkdir()
        for i,p in enumerate(paths):
            copytex(p,tFolder)
            file = Path(p)
            paths[i] = (tFolder +'/'+ file.name).replace('\\','/')  #pathsを変える
    if input[3]:
        errors = 0
        for i,p in enumerate(paths):
            new = convertRelative(mFolder,p,input[3])
            if new == None:
                return()
            paths[i] = new
    save_xml(mxnodes,paths,filename,mFolder,scl,isfile,newattr)

def tex(nodes,paths,elemNG,isfile):
    elemNGtex = []
    elemNGtex_1 = []
    elemNGtex_2 = []
    minus=0
    for i,node in enumerate(nodes):
        if isfile[i]==0:
            minus += 1
            continue
        i -= minus
        elemNGtex.append(ET.SubElement(elemNG, 'image'))
        elemNGtex[i].set('name',node)
        if node in ['base_color','opacity']:    
            elemNGtex[i].set('type','color3')
        elif node == 'normal':
            elemNGtex[i].set('type','vector3')
        else:
            elemNGtex[i].set('type','float')
        elemNGtex_1.append(ET.SubElement(elemNGtex[i], 'input'))
        elemNGtex_1[i].set('name','texcoord')
        elemNGtex_1[i].set('type','vector2')
        elemNGtex_1[i].set('nodename','node_texcoord')
        elemNGtex_2.append(ET.SubElement(elemNGtex[i], 'input'))
        elemNGtex_2[i].set('name','file')
        elemNGtex_2[i].set('type','filename')
        elemNGtex_2[i].set('value',paths[i])
        if node in ['base_color','opacity']:
            elemNGtex_2[i].set('colorspace','srgb_texture')
        else:
            elemNGtex_2[i].set('colorspace','Raw')
        if node == 'normal':
            elemNGtex_3 = (ET.SubElement(elemNG, 'normalmap'))
            elemNGtex_3.set('name','normalMap')
            elemNGtex_3.set('type','vector3')
            elemNGtex_4 = (ET.SubElement(elemNGtex_3, 'input'))
            elemNGtex_4.set('name','in')
            elemNGtex_4.set('type','vector3')
            elemNGtex_4.set('nodename','normal')


def out(nodes,elemNG,isfile):
    elemNGout=[]
    minus=0
    for i,node in enumerate(nodes):
        if isfile[i]==0:
            minus += 1
            continue
        i -= minus
        elemNGout.append(ET.SubElement(elemNG, 'output'))
        elemNGout[i].set('name',node+'_out')
        if node in ['base_color','opacity']:
            elemNGout[i].set('type','color3')
        elif node == 'normal':
            elemNGout[i].set('type','vector3')
            node = 'normalMap'
        else:
            elemNGout[i].set('type','float')
        elemNGout[i].set('nodename',node)

def ss(nodes,root,scl,isfile,newattr):
    elemNGss = ET.SubElement(root, 'standard_surface')
    elemNGss.set('name','SR_standard_surface')
    elemNGss.set('type','surfaceshader')
    elemNGss_1 = []
    for i,node in enumerate(nodes):
        if node in 'height':
            elemNGdis = ET.SubElement(root, 'displacement')
            elemNGdis.set('name','SR_displacement')
            elemNGdis.set('type','displacementshader')
            elemNGdis_1 = ET.SubElement(elemNGdis, 'input')
            elemNGdis_1.set('name','displacement')
            elemNGdis_1.set('type','float')
            elemNGdis_1.set('nodegraph','NG_input')
            elemNGdis_1.set('output',node+'_out')
            elemNGdis_h= ET.SubElement(elemNGdis, 'input')
            elemNGdis_h.set('name','scale')
            elemNGdis_h.set('type','float')
            elemNGdis_h.set('value',str(scl))
            continue
        if isfile[i]==0:
            elemNGss_1.append(ET.SubElement(elemNGss, 'input'))
            elemNGss_1[i].set('name',str(newattr[i][0]))
            elemNGss_1[i].set('type',str(newattr[i][1]))
            elemNGss_1[i].set('value',str(newattr[i][2]))
            continue
        elemNGss_1.append(ET.SubElement(elemNGss, 'input'))
        elemNGss_1[i].set('name',node)
        if node in ['base_color','opacity']:
            elemNGss_1[i].set('type','color3')
        elif node == 'normal':
            elemNGss_1[i].set('type','vector3')
        else:
            elemNGss_1[i].set('type','float')
        elemNGss_1[i].set('nodegraph','NG_input')
        elemNGss_1[i].set('output',node+'_out')

def mat(root,nodes):
    elemNGmat = ET.SubElement(root, 'surfacematerial')
    elemNGmat.set('name','material')
    elemNGmat.set('type','material')
    elemNGmat_1 = ET.SubElement(elemNGmat, 'input')
    elemNGmat_1.set('name','surfaceshader')
    elemNGmat_1.set('type','surfaceshader')
    elemNGmat_1.set('nodename','SR_standard_surface')
    if 'height' in nodes:
        elemNGmat_2 = ET.SubElement(elemNGmat, 'input')
        elemNGmat_2.set('name','displacementshader')
        elemNGmat_2.set('type','displacementshader')
        elemNGmat_2.set('nodename','SR_displacement')

def save_xml(nodes,paths,s,mFolder,scl,isfile,newattr):
    root = ET.Element('materialx')
    root.set('version','1.38')
    elemNG = ET.SubElement(root, 'nodegraph')
    elemNG.set('name','NG_input')
    # Texcoord作成
    elemNG.append(ET.Comment('TexCoord'))
    elemNGtc = ET.SubElement(elemNG, 'texcoord')
    elemNGtc.set('name','node_texcoord')
    elemNGtc.set('type','vector2')
    # テクスチャ呼び出し
    elemNG.append(ET.Comment('Texture'))
    tex(nodes,paths,elemNG,isfile)
    # アウトプット
    elemNG.append(ET.Comment('Output'))
    out(nodes,elemNG,isfile)
    # サーフェイスシェーダー
    ss(nodes,root,scl,isfile,newattr)
    # マテリアル
    mat(root,nodes)
    # インデントを付けて保存
    tree = ET.ElementTree(root)
    ET.indent(tree, '  ')
    tree.write(mFolder+'\\'+s+'.mtlx',encoding='utf-8',xml_declaration=True)

def overwrite():
    ErrorWindow(5)

# マテリアルの名前を取得
def getname(self):
    s = cmds.ls(sl=True)
    if checkname(s) != False:
        self.textbox2.setText(s[0])
# 正しいマテリアルが選択されているか
def checkname(s):
    if s == []:
        ErrorWindow(6)
        return(False)
    if  cmds.objectType(s[0]) not in ['aiStandardSurface','standardSurface']:
        ErrorWindow(7)
        return(False)
    return(True)

def closeOldWindow(title):
    for widget in QtWidgets.QApplication.topLevelWidgets():
        if title == widget.windowTitle():
           widget.deleteLater()
           widget.close()

#  アプリの実行と終了
def openWindow():
    title = "MaterialX_Convert"
    closeOldWindow(title)
    
    app = QtWidgets.QApplication.instance()
    qm_file = r"mtlx_Jp.qm"
    
    translator = QtCore.QTranslator(app)
    translator.load(qm_file,directory = cmds.workspace(q=True,rootDirectory=True)+'\\scripts\\i18n')
    QtCore.QCoreApplication.installTranslator(translator)
    
    window = MainWindow(title,translator)
    window.show()
    app.exec_()
    
if __name__ == "__main__":
    openWindow()
