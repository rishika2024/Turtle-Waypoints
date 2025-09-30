from setuptools import find_packages, setup

package_name = 'turtle_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/waypoints.launch.xml']),
        ('share/' + package_name + '/config', ['config/colors.yaml'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rishika2024',
    maintainer_email='berarishika@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'waypoint = turtle_control.waypoint:main'
        ],
    },
)
