#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

# 支持替换的资源类型
data_type_tuple = ["anim", "array", "attr", "bool", "color", "dimen", "drawable", "id", "integer",
                   "layout", "menu", "string", "style", "styleable", "xml", "raw"]


def replaceCodeImport(srcPathList, package, RPackageName):
    """
    替换java文件中的import R类为AutoR

    替换java文件中的R.id/string/layout……等引用为AutoR.id/string/layout……

    :param srcPathList:源码文件夹

    :param package:工程包名

    :param RPackageName:AutoR所在位置包名
    """
    srcImportString = 'import ' + package + '.R;'
    replaceImportString = 'import ' + RPackageName + '.AutoR;'
    for srcPath in srcPathList:
        for parent, _, fileNames in os.walk(srcPath):
            for temp in fileNames:
                if not temp.endswith('.java'):
                    continue
                codeFile = os.path.join(parent, temp)
                # open and read the file
                with open(codeFile, 'r') as fp:
                    codeFileContent = fp.readlines()

                isChanged = False
                for index in range(len(codeFileContent)):
                    thisLine = codeFileContent[index]

                    # 替换import代码
                    if thisLine.find(srcImportString) != -1:
                        codeFileContent[index] = thisLine.replace(srcImportString,
                                                                  replaceImportString)
                        isChanged = True
                    else:
                        # 替换资源引用代码
                        for data_type in data_type_tuple:
                            # 考虑一行中多个R.string,android.R.string,等问题
                            zz = f'[^.^\w]R\.{data_type}\.'
                            # print(f'=finding: {data_type}==')
                            # print(re.findall(zz, thisLine))
                            pattern = re.compile(zz)
                            result = re.findall(pattern, thisLine)
                            if len(result) > 0:
                                replaceList = [x.replace('R.', 'AutoR.') for x in result]
                                for replace in replaceList:
                                    # print('doing replace:'+replace)
                                    thisLine = re.sub(zz, replace, thisLine)
                                    # print(thisLine)
                                    codeFileContent[index] = re.sub(pattern, 'AutoR.', thisLine)
                                    isChanged = True

                if isChanged:
                    print('replacing file ' + temp)
                    with open(codeFile, 'w') as fp:
                        fp.writelines(codeFileContent)


def replace_quote(codeFileContent, index):
    """
    替换R引用
    """
    thisLine = codeFileContent[index]
    for data_type in data_type_tuple:
        # 考虑一行中多个R.string,android.R.string,等问题
        zz = f'[^.^\w]R\.{data_type}\.'
        # print(f'=finding: {data_type}==')
        # print(re.findall(zz, thisLine))
        pattern = re.compile(zz)
        result = re.findall(pattern, thisLine)
        if len(result) > 0:
            replaceList = [x.replace('R.', 'AutoR.') for x in result]
            for replace in replaceList:
                # print('doing replace:'+replace)
                thisLine = re.sub(zz, replace, thisLine)
                # print(thisLine)
                codeFileContent[index] = re.sub(pattern, 'AutoR.', thisLine)
                return True


if __name__ == '__main__':
    testLine = '+ (CashierConst.CR.equalsIgnoreCase(mCardType) ? ResUtils.getString(R.string.wifipay_credit_card),ResUtils.getString(R.layout.wifipay_credit_card) ' \
               'ResUtils.getString(android.R.string.wifipay_credit_card)'
    # testLine = '(3R.string.wifipay_credit_card)'
    for data_type in data_type_tuple:
        zz =f'[^.^\w]R\.{data_type}\.'
        print(f'=finding: {data_type}==')
        print(re.findall(zz, testLine))
        # pattern = re.compile(zz)
        # result = re.findall(pattern, testLine)
        # if len(result) > 0:
        #     replaceList = [x.replace('R.', 'AutoR.') for x in result]
        #     for replace in replaceList:
        #         print('doing replace:'+replace)
        #         testLine = re.sub(zz, replace, testLine)
        #         print(testLine)
