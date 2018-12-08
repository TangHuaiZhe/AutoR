#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import configparser
import os
import xml.dom.minidom
import re


# 获取配置文件解释器
def getConfigParser():
    configFile = os.path.join(os.path.dirname(__file__), 'config.ini')
    if os.path.exists(configFile):
        parser = configparser.ConfigParser()
        parser.read(configFile)
        return parser


# 判断是否是Eclipse的工程
# def isEclipseProject(projectDir):
#     manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
#     return os.path.exists(manifestFile)


# 判断是否是AndroidStudio的工程
def isAndroidStudioProject(projectDir):
    manifestFile = os.path.join(projectDir, 'AndroidManifest.xml')
    gradleFile = os.path.join(projectDir, 'build.gradle')
    if os.path.exists(manifestFile):
        return False
    else:
        return os.path.exists(gradleFile)


def getDefaultAaptFile(sdkdir):
    toolsPath = os.path.join(sdkdir, 'build-tools')
    if os.path.exists(toolsPath):
        _, dirNames, _ = os.walk(toolsPath).next()
        if len(dirNames) != 0:
            verPath = os.path.join(toolsPath, dirNames[0])
            aaptPath = os.path.join(verPath, 'aapt')
            print('aapt is at ' + aaptPath)
            return aaptPath


def getDefaultAndroidjarFile(sdkdir):
    platformPath = os.path.join(sdkdir, 'platforms')
    if os.path.exists(platformPath):
        _, dirNames, _ = os.walk(platformPath).next()
        if len(dirNames) != 0:
            verPath = os.path.join(platformPath, dirNames[0])
            androidjarPath = os.path.join(verPath, 'android.jar')
            print('android.jar is at ' + androidjarPath)
            return androidjarPath


def getAaptFile(sdkdir, buildVersion):
    toolsPath = os.path.join(sdkdir, 'build-tools')
    verPath = os.path.join(toolsPath, buildVersion)
    aaptPath = os.path.join(verPath, 'aapt')
    print('aapt is at ' + aaptPath)
    return aaptPath


def getAndroidjarFile(sdkdir, compileSdkVersion):
    platformPath = os.path.join(sdkdir, 'platforms')
    verPath = os.path.join(platformPath, 'android-' + compileSdkVersion)
    androidjarPath = os.path.join(verPath, 'android.jar')
    print('android.jar is at ' + androidjarPath)
    return androidjarPath


def getIsLibraryProject(projectDir):
    """
    是否是library工程
    """
    # 对Eclipse工程，在工程目录的project.properties文件中配置有该工程是否是library工程的标记
    # android.library=true
    isLibrary = False
    settingFile = os.path.join(projectDir, 'build.gradle')
    if os.path.exists(settingFile):
        regex = re.compile(r"^\s*apply plugin:\s*'com\.android\.(\S+)'")
        with open(settingFile, 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                ret = regex.search(line)
                if ret:
                    libraryTag = ret.group(1).strip()
                    if libraryTag == 'library':
                        isLibrary = True
                    elif libraryTag == 'application':
                        isLibrary = False
                    print('This is a library project? ' + str(isLibrary))
                    return isLibrary


def getRPath(projectDir):
    path = os.path.join(projectDir,
                        'build' + os.path.sep + 'generated' + os.path.sep + 'source' + os.path.sep + 'r' + os.path.sep + 'release')
    print('The R.java is in to generate at ' + path)
    return path


def getResPath(projectDir):
    path = os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'res')
    print('The project res path is ' + path)
    return path


def getManifestFile(projectDir):
    manifestFile = os.path.join(projectDir,
                                'src' + os.path.sep + 'main' + os.path.sep + 'AndroidManifest.xml')
    print('The manifest file is ' + manifestFile)
    return manifestFile


def getPackageName(projectDir):
    manifestFile = getManifestFile(projectDir)
    if os.path.exists(manifestFile):
        # 解析xml文件
        dom = xml.dom.minidom.parse(manifestFile)
        # 找出manifest节点
        manifestNodeList = dom.getElementsByTagName('manifest')
        if len(manifestNodeList) == 1:
            manifestNode = manifestNodeList[0]
            packageName = manifestNode.getAttribute('package')
            print('The package name is ' + packageName)
            return packageName


def getRClassFile(projectDir, RPath):
    packageName = getPackageName(projectDir)
    if packageName is not None and packageName != '':
        splitPackageName = packageName.split('.')
        RClassFile = RPath
        for splitItem in splitPackageName:
            RClassFile = os.path.join(RClassFile, splitItem)
        RClassFile = os.path.join(RClassFile, 'R.java')
        print('The generated R.java is ' + RClassFile)
        return RClassFile


# todo 适配多渠道
def getSrcPathList(projectDir):
    srcPath = [os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java')]
    return srcPath


def getDestRClassPath(projectDir, destRClassPackage):
    destRClassPath = os.path.join(projectDir, 'src' + os.path.sep + 'main' + os.path.sep + 'java')
    splitPackageName = destRClassPackage.split('.')
    for splitItem in splitPackageName:
        destRClassPath = os.path.join(destRClassPath, splitItem)
    print('The new R.java is ' + destRClassPath)
    return destRClassPath


def getEnvironment(sdkdir):
    """
    获取环境变量 aapt和android.jar
    """
    buildVersion = getConfigParser().get('Version', 'buildVersion')
    compileSdkVersion = getConfigParser().get('Version', 'compileSdkVersion')

    # 获取android sdk中的aapt文件路径和android.jar文件路径
    aaptFile = getAaptFile(sdkdir, buildVersion)
    androidjar_file = getAndroidjarFile(sdkdir, compileSdkVersion)
    # 获取不到文件，或者文件不存在，返回
    if aaptFile is None or not os.path.exists(aaptFile):
        raise RuntimeError('Cannot find aapt in ' + sdkdir)
    if androidjar_file is None or not os.path.exists(androidjar_file):
        raise RuntimeError('Cannot find android.jar in ' + sdkdir)
    return aaptFile, androidjar_file


def writeToFile(filePath, fileContentList):
    # 写入目标R类所在的目录
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    destRClassFile = os.path.join(filePath, 'AutoR.java')
    destRClassFp = codecs.open(destRClassFile, 'w', 'utf-8')
    destRClassFp.writelines(fileContentList)
    destRClassFp.close()
