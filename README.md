## Pycogram

Pycogram is a simple password manager written in Python.

### Quick example

1. Clone this repo.
2. In the root directory, run `python run_pycogram.py -n` to create a new keystore.
3. Run, for example, `python run_pycogram.py -a google -a wikipedia` to add a key-value pair to the groups "google" and "wikipedia".
4. Enter a key-password pair for each.
5. You're done! To extract passwords, simply use `python run_pycogram.py -e <group>`.

Sample output (line breaks added for readability):

```
/pycogram$ python run_pycogram.py -n

Please enter the master key for your new password store twice.
Master key: (I entered qwer here) 
Confirm:  (qwer here too)

.PYCOGRAM_STORE.json successfully created.

/pycogram$ python run_pycogram.py -a google -a wikipedia

Please enter your master key.
Master key: (qwer)

Please enter the key you wish to create in group google.
Key: my_email

Please enter the password you wish to associate with the key my_email.
Password: (password_1)

Please enter the key you wish to create in group wikipedia.
Key: my_wiki

Please enter the password you wish to associate with the key my_wiki.
Password: (password_2)
Changes written to .PYCOGRAM_STORE.json successfully.

/pycogram$ python run_pycogram.py -e google -e wikipedia

Please enter your master key.
Master key: (qwer)
 
Please enter the key in group google associated with the desired password.
Key: my_email
The associated password is: password_1

Please enter the key in group wikipedia associated with the desired password.
Key: my_wiki
The associated password is: password_2
```

### Overview

 Pycogram encrypts passwords in the form of *key-value pairs*, where keys represent usernames, or the equivalent, and values represent passwords. Key-value pairs are placed into *groups*, which represent websites, applications, etc..

As an aside, it's called Pycogram because I wanted to do the pi -> py thing, and it's basically the homebrewed opposite, technically speaking, of Google's password manager (since a googol is huge and a picogram is tiny). There's actually another package named pycogram, but I'm not going to put this on PyPI, so I don't think anyone will mind.

The current nature of the encryption (simple XOR) means that values which were similar pre-encryption will also be similar post-encryption. A possible example:

```python
encrypt('bake') == '@ÄÐS' 
encrypt('cake') == 'AÄÐS' 
```  

Also, since there's no padding (that would be trivial to do, I think...? Hm.), the length of the ciphertext is always equal to the length of the plaintext.  

This is a small side project (about 4 hours' worth of work) meant more as an experiment than as an actual secure utility; I believe the conventional wisdom, when it comes to encryption, is to use an open-source industry-tested standard, and that certainly makes sense. 
 
Nevertheless, if practical, I would like to revisit this in the future to make it difficult for a casual attacker to break (perhaps something like TEA?), more as an exercise in coding and software engineering than anything else.

### Current to-do (read: may never happen) list:

* Implement key-value pair replacement and deletion
* Implement "interactive mode"
* Write more tests
* Expand encryption scheme beyond simple XOR

### Problems I foresee:

* Insecure input

The master encryption/decryption key is stored in memory as plaintext. Given how high-level Python is, I'm not sure if there's a way to prevent this without writing a C extension or something. Low-probability future project.

* Separation of concerns

The application layer - `run_pycogram.py` - should not contain functions or complex behaviour; such logic should be factored out into modules which are imported. Right now, a fair amount of IO needs to be done, such as when checking for an existing keystore file. It should be factored out into an `iolib` module.

* Functional style in the application layer

Right now, the non-exclusive flags (other than `-i` and `-n`) are run sequentially; you can add, then remove, then list, etc.. This screws with the functional style; see how reassignment is performed in the `add` block, due to having to take IO. This is ugly; if the IO logic is encapsulated in the suggested `iolib` module, the application layer could be cleaned up in terms of implementation. 

* Feature creep

Always a problem.

### Cool things I learnt/played with

* Separation of argument parsing *logic* and *specification* (`argument_spec.json`) - something I thought of a while ago, but never got round to trying
* Some bitwise manipulation of strings (the aforementioned XOR)
* Basic hashing/encryption
