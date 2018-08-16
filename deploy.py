# encoding:utf-8
# 使用方法：
# python deploy.py --projectPath D:\qw --projectName daijiguo --hostAndPort 192.168.0.29:8080
import argparse


import re
import subprocess

# step1 接收外部传参
def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--projectPath', type=str, help='source/java path')
    parser.add_argument('--hostAndPort', type=str, help='host and port')
    parser.add_argument('--projectName', type=str, help='project name')

    args = parser.parse_args()
    projectPath = args.projectPath
    host = args.hostAndPort
    projectName = args.projectName
    return projectPath, host, projectName

# 配置header.jsp和shiro.properties
def configHost(projectPath, host, projectName):
    headerPath = projectPath + '/WebRoot/WEB-INF/jsp/site/include/header.jsp'
    shiroPath = projectPath + '/src/main/resources/shiro.properties'
    pomPath = projectPath + '/pom.xml'

    # 替换header.jsp中的host:port
    with open(headerPath, "r+", 1) as f:
        newFile = re.sub(r'sitePath[\s\S]*?\";', r'sitePath = "http://' + host + '/' + projectName + '/";', f.read())
        newFile = re.sub(r'backPath[\s\S]*?\";', r'backPath = "http://' + host + '/' + projectName + '/";', newFile)
        newFile = re.sub(r'basePath[\s\S]*?\";', r'basePath = "http://' + host + '/' + projectName + '/";', newFile)
    with open(headerPath, "w", 1) as f:
        f.write(newFile)
    # 替换shiro.properties中的host:port
    with open(shiroPath, "r+", 1) as f:
        newFile = re.sub(r'http://.*?/cas', r'http://' + host + '/cas', f.read())
        newFile = re.sub(r'service=http://.*?/shiro-cas', r'service=http://' + host + '/' + projectName + '/shiro-cas',
                         newFile)
    with open(shiroPath, "w", 1) as f:
        f.write(newFile)

    # 替换pom.xml中的<warName>
    with open(pomPath, "r+", 1) as f:
        newFile = re.sub(r'<warName>.*?</warName>', r'<warName>'+projectName+'</warName>', f.read(), 1)
    with open(pomPath, "w", 1) as f:
        f.write(newFile)
    return pomPath


# 执行mvn war
def mvnWar(pomPath, projectPath):
    mvnShell = 'cd /d '+ projectPath + '&&mvn clean&&mvn --file ' + pomPath + ' package'
    mvnResult = subprocess.check_output(mvnShell, shell=True)
    outPath = re.search(r'Building war:([\s\S]*?\.war)', mvnResult).group(1)
    return outPath


if __name__ == '__main__':
    projectPath, host, projectName = getArgs()
    pomPath = configHost(projectPath, host, projectName)
    outPath = mvnWar(pomPath, projectPath)
    print 'the path of ' + projectName + '.war: '+outPath
