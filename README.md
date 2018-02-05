# LDA - Latent Dirichlet Analysis

An Azure-ready implementation of LDA in Python using Scikit.

# General Description

Topic Modelling is a statistical method that attempts to identify common topics in large bodies of text. 

It is an unsupervised method which means that it doesn't require any labelled data. It does however require a little bit of interpretation of the results. The technique is able to identify word groups that are commonly found together but it is not able to label them itself.

Example output (from a 100,000 customer survey corpus):

 * 'great', 'easy’, 'problem’
 * 'good', 'service', 'customer’
 * 'use’, 'account', 'card’
 * 'products', 'like', 'love’ 
 * 'website', 'problems', 'order’,
 * 'did', 'phone', 'new’, 
 * 'store', 'went’, 'didn’t’, 
 * 'food’, 'nice', 'shop’
 * 'online', 'time', 'bought’, 
 * 'staff', 'helpful', 'friendly'

It's up to the user to interpret what the topics actually are but hopefully it can be seen that some obvious candidates easily suggest themselves: 'problems using a website', "good customer service", "helpful staff" and so on.

# Implementation

The LDA implementation is behind a Flask-based HTTP host. A json representation of the data, as a list of strings, is first written to Azure Blob storage and a request on the webserver made detailing the location of the new data. The server responds immediately with a UUID which references the job and creates a corresponding row in Azure Table storage tracking the job's progress.

When complete the Table row status is updated. Clients wishing to track the job status can simply poll the relevant Table row.

# Deployment

Details about deploying a Flask-based web app to Azure can be found here: https://docs.microsoft.com/en-us/azure/app-service/app-service-web-get-started-python

--
end
