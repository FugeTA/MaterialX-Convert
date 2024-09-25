import maya.cmds as cmds
from functools import partial
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import shutil

def convertRelative(target,current):
    absp = Path(current).resolve()
    try:
        relp = absp.relative_to(target)
    except ValueError:
        cmds.confirmDialog(t='Error',m=('Path is not in the subpath'),b='close')
        return()
    return(str(relp).replace('\\','/'))

def newAttr(ws,*args):
    s=checkname()
    if s == False:
        return
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
            if isinstance(value,float):
                type = 'float'
            elif isinstance(value,list):
                type = 'color3'
                value = str(value[0][0])+', '+str(value[0][1])+', '+str(value[0][2])
            else:
                type = 'boolean'
                value = str.lower(str(value))
            newattr.append([mxattr[i],type,value])
            mxnodes.append(mxattr[i])
            ssnodes.append(attr)
    if newattr==[]:
        err = cmds.confirmDialog(t='Error',m='This material is the default.\nCreation has stopped',b='Close')
        return
    getNodePath(ssnodes,mxnodes,newattr,ws,s)

def copytex(bfile,afolder):
    shutil.copy(bfile,afolder)

def getNodePath(ssnodes,mxnodes,newattr,ws,s):
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
    mFolder = cmds.textField(ws['mainpath'],q=True,tx=True)
    mFolder = str(mFolder.replace('/','\\'))
    tFolder = cmds.textField(ws['texpath'],q=True,tx=True)

    filename = cmds.textField(ws['mtlxname'],q=True,tx=True)
    if cmds.checkBox(ws['check1'],q=True,v=True):
        path=Path(tFolder)
        if not path.is_dir():
            Path.makedirs(tFolder)
        for i,p in enumerate(paths):
            copytex(p,tFolder)
            file = Path(p)
            paths[i] = (tFolder +'/'+ file.name).replace('\\','/')  #pathsを変える
    if cmds.checkBox(ws['check2'],q=True,v=True):
        for i,p in enumerate(paths):
            new = convertRelative(mFolder,p)
            if new == '':
                break
            paths[i] = convertRelative(mFolder,p)
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
        if node in ['base_color','opacity','normal']:
            elemNGtex_2[i].set('colorspace','srgb_texture')

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

def wndisable(ws,*args):
    if cmds.checkBox(ws['check1'],q=True,v=True):
        cmds.textField(ws['texpath'],e=True,en=True)
        cmds.button(ws['button3'],e=True,en=True)
    else:
        cmds.textField(ws['texpath'],e=True,en=False)
        cmds.button(ws['button3'],e=True,en=False)

def getPath(ws,n,*args):
    if n:
        path = cmds.fileDialog2(fm=3,okc='Select',dir=(cmds.textField(ws['mainpath'],q=True,tx=True)))
        cmds.textField(ws['mainpath'],e=True,tx=str(path[0]))
        cmds.textField(ws['texpath'],e=True,tx=str(path[0])+'/textures')
    else:
        path = cmds.fileDialog2(fm=3,okc='Select',dir=(cmds.textField(ws['texpath'],q=True,tx=True)))
        cmds.textField(ws['texpath'],e=True,tx=str(path[0]))

def overwrite():
    cmds.confirmDialog(t='Warning',m='File has already exists.\nDo you want to replace it?',b=['Yes','No'])

def getname(ws,*args):
    s = cmds.ls(sl=True)
    if checkname() != False:
        cmds.textField(ws['mtlxname'],e=True,tx=s[0])
        
def checkname():
    s = cmds.ls(sl=True)
    if s==[]:
        cmds.confirmDialog(t='Error',m='Please select a Material.',b='Close')
        return(False)
    if  cmds.objectType(s[0]) not in ['aiStandardSurface','standardSurface']:
        cmds.confirmDialog(t='Error',m='Please select a StandardSurface Material.',b='Close')
        return(False)
    return(s)

def makeWindow():
    project = cmds.workspace(q=True,fn=True)
    winname = 'MaterialX_Convert'
    if cmds.window(winname,q=True,ex=True)==True:  # すでにウィンドウがあれば閉じてから開く
        cmds.deleteUI(winname,window=True)
    cmds.window(winname,s=True,rtf=True)  # ウィンドウの作成
    ws={}
    cmds.columnLayout()
    cmds.frameLayout(l='Save folder')
    ws['check2'] = cmds.checkBox(l='Relative path') 
    cmds.rowLayout(nc=2)
    ws['mainpath'] = cmds.textField(text=project)
    ws['button1'] = cmds.button(l='Select folder',c=partial(getPath,ws,1))
    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout(l='File name')
    cmds.rowLayout(nc=2)
    ws['mtlxname'] = cmds.textField(text='standardSurface')
    ws['button2'] = cmds.button(l='Use material name',c=partial(getname,ws))
    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout(l='TextureCopy')    
    ws['check1'] = cmds.checkBox(l='Copy texture file',cc=partial(wndisable,ws)) 
    
    cmds.rowLayout(nc=2)
    ws['texpath'] = cmds.textField(text=project+'\\textures',en=False)
    ws['button3'] = cmds.button(l='Select folder',c=partial(getPath,ws,0),en=False)
    cmds.setParent('..')
    
    cmds.button(l='Create',c=partial(newAttr,ws))
    
    cmds.setParent('..')

    cmds.showWindow(winname)
makeWindow()
