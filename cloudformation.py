from troposphere.route53 import RecordSetType
from troposphere.s3 import Bucket, PublicRead

from troposphere import GetAtt, Join, Output,FindInMap 
from troposphere import Parameter, Ref, Template, Equals
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.cloudfront import ForwardedValues
from troposphere.cloudfront import S3Origin
from troposphere import ec2


t = Template()

t.add_description("PyCon Cloudformation Template test")

envType = Parameter(
	"EnvType",
	Type="String",
	AllowedValues=["prod","test"],
	ConstraintDescription="must specify prod or test."
)

t.add_parameter(envType)

t.add_mapping('RegionMap', {
	"us-east-1"      : { "AMI" : "ami-7f418316", "TestAz" : "us-east-1a" },
    "us-west-1"      : { "AMI" : "ami-951945d0", "TestAz" : "us-west-1a" },
    "us-west-2"      : { "AMI" : "ami-16fd7026", "TestAz" : "us-west-2a" },
    "eu-west-1"      : { "AMI" : "ami-24506250", "TestAz" : "eu-west-1a" },
    "sa-east-1"      : { "AMI" : "ami-3e3be423", "TestAz" : "sa-east-1a" },
    "ap-southeast-1" : { "AMI" : "ami-74dda626", "TestAz" : "ap-southeast-1a" },
    "ap-southeast-2" : { "AMI" : "ami-b3990e89", "TestAz" : "ap-southeast-2a" },
    "ap-northeast-1" : { "AMI" : "ami-dcfa4edd", "TestAz" : "ap-northeast-1a" }
})

conditions = {
	"CreateProdResources": Equals(Ref("EnvType"), "prod")
}

t.add_condition("CreateProdResources", conditions["CreateProdResources"])

resources = {
	"EC2Instance": ec2.Instance(
		"EC2Instance",
		ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
	),
	"NewVolume": ec2.Volume(
		"NewVolume",
		Condition="CreateProdResources",
		Size=100,
		AvailabilityZone=GetAtt("EC2Instance","AvailabilityZone")
	),
	"MountPoint": ec2.VolumeAttachment(
		"MountPoint",
		Condition="CreateProdResources",
		InstanceId=Ref("EC2Instance"),
		VolumeId=Ref("NewVolume"),
		Device="/dev/sdh"
	)
}

outputs = {
	"VolumeId": Output(
		"VolumeId",
		Value=Ref(resources["NewVolume"]),
		Condition="CreateProdResources"
	)
}

for r in resources.values():
	t.add_resource(r)
for output in outputs.values():
	t.add_output(output)

print(t.to_json())

