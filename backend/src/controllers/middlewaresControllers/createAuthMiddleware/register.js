const Joi = require('joi');
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const { generate: uniqueId } = require('shortid');

const register = async (req, res, { userModel }) => {
    const UserPasswordModel = mongoose.model(userModel + 'Password');
    const UserModel = mongoose.model(userModel);
    const { email, password, name, surname, country } = req.body;

    // validate
    const objectSchema = Joi.object({
        email: Joi.string()
            .email({ tlds: { allow: true } })
            .required(),
        password: Joi.string().required(),
        name: Joi.string().required(),
        surname: Joi.string().allow(''),
        country: Joi.string().allow(''),
    });

    const { error } = objectSchema.validate({ email, password, name, surname, country });
    if (error) {
        return res.status(409).json({
            success: false,
            result: null,
            error: error,
            message: 'Invalid/Missing credentials.',
            errorMessage: error.message,
        });
    }

    const existingUser = await UserModel.findOne({ email: email, removed: false });

    if (existingUser)
        return res.status(409).json({
            success: false,
            result: null,
            message: 'An account with this email already exists.',
        });

    const salt = uniqueId();
    const passwordHash = bcrypt.hashSync(salt + password);

    const newUser = new UserModel({
        email,
        name,
        surname,
        country,
        enabled: true,
    });

    const result = await newUser.save();

    const UserPasswordData = {
        password: passwordHash,
        emailVerified: true,
        salt: salt,
        user: result._id,
    };

    await new UserPasswordModel(UserPasswordData).save();

    return res.status(200).json({
        success: true,
        result: {
            _id: result._id,
            name: result.name,
            surname: result.surname,
            role: result.role,
            email: result.email,
        },
        message: 'Successfully registered user',
    });
};

module.exports = register;
