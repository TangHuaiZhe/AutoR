#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tool
from codeTime import clock
import os
import resourceProcess as rp
import codeTool
import datetime


# 配置的是项目/Library路径，aapt 打包资源文件
def processProjectDir(projectDir, sdkdir, destRClassPackage):
    # 是否Library
    isLibrary = tool.getIsLibraryProject(projectDir)
    # 获取aapt环境变量
    aaptFile, androidJarFile = tool.getEnvironment(sdkdir)
    # 打包原生的R.java
    RClassFile = aaptRClass(aaptFile, androidJarFile, isLibrary, projectDir)
    # 生成AutoR的源码
    newRLines = rp.convertR(isLibrary, RClassFile, destRClassPackage)
    # AutoR的路径
    autoR_Path = tool.getDestRClassPath(projectDir, destRClassPackage)
    # 写入AutoR
    tool.writeToFile(autoR_Path, newRLines)
    # 替换源码中的R引用
    replaceCode(destRClassPackage, projectDir)


# 通过aapt生成R.java类路径，项目中res文件夹路径和AndroidManifest.xml文件路径
def aaptRClass(aaptFile, androidjarFile, isLibrary, projectDir):
    RPath = tool.getRPath(projectDir)
    resPath = tool.getResPath(projectDir)
    manifestFile = tool.getManifestFile(projectDir)
    if not os.path.exists(RPath):
        os.makedirs(RPath)
    if not os.path.exists(resPath) or not os.path.exists(manifestFile):
        raise RuntimeError('Cannot find resPath or manifest file in ' + projectDir)
    # 判断工程是否是Library工程
    command = aaptFile + ' p -m -J ' + RPath + ' -S ' + resPath + ' -M ' + manifestFile + ' -I ' + androidjarFile
    # 对Library工程需要添加参数--non-constant-id，这样生成的R.java中的资源id就是public static int，否则是public static final int
    if isLibrary:
        command += ' --non-constant-id'
    print('Try to execute command: ' + command)
    '''
        /Users/tang/Library/Android/sdk/build-tools/27.0.3/aapt p -m -J 
        /Users/tang/Code/open-wallet-sdk333/walletsdk_common/build/generated/source/r/release
        -S /Users/tang/Code/open-wallet-sdk333/walletsdk_common/src/main/res 
        -M /Users/tang/Code/open-wallet-sdk333/walletsdk_common/src/main/AndroidManifest.xml 
        -I /Users/tang/Library/Android/sdk/platforms/android-27/android.jar 
        --non-constant-id
        '''
    ret = os.system(command)
    if ret != 0:
        print('Find errors in resource folder')
        exit(1)
    # 获取生成的R.java文件路径
    RClassFile = tool.getRClassFile(projectDir, RPath)
    if not os.path.exists(RClassFile):
        raise RuntimeError('R class is not generated')
    return RClassFile


# 替换代码中的import R类和资源引用
def replaceCode(destRClassPackage, projectDir):
    if tool.getConfigParser().has_option('RClass', 'ReplaceCode'):
        isReplace = tool.getConfigParser().get('RClass', 'ReplaceCode')
        if isReplace.lower() == 'true':
            package = tool.getPackageName(projectDir)
            if package == destRClassPackage:
                print('the package name is the same, and no need to replace')
            srcPathList = tool.getSrcPathList(projectDir)
            codeTool.replaceCodeImport(srcPathList, package, destRClassPackage)


@clock
def process():
    configParser = tool.getConfigParser()
    if configParser is None:
        raise RuntimeError('Get parser failed')

    ProjectOrResDir = os.path.abspath(
        os.path.join(os.getcwd(), "..")) + os.path.sep + configParser.get('Dir', 'ProjectOrResDir')
    # ProjectOrResDir = '/Users/tang/Code/open-wallet-sdk2222/SdpOpenWallet'
    sdkdir = os.environ.get('ANDROID_HOME')

    if sdkdir is None:
        sdkdir = configParser.get('Dir', 'sdkdir')
        print('you should define ANDROID_HOME in your pc')

    # 获取目标R类的路径
    destRClassPackage = configParser.get('RClass', 'RClassPackage').strip('.')
    # 没有相应配置，返回
    if not os.path.exists(sdkdir) or not os.path.exists(ProjectOrResDir):
        raise RuntimeError(
            'sdkdir or ProjectOrResDir Invalid parameters' + sdkdir + '\n' + ProjectOrResDir)

    isAndroidStudio = tool.isAndroidStudioProject(ProjectOrResDir)
    if not isAndroidStudio:
        raise RuntimeError('is not AndroidStudio project')

    processProjectDir(ProjectOrResDir, sdkdir, destRClassPackage)


# 入口
if __name__ == '__main__':
    process()
